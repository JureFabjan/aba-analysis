""" Expression Value Comparison

In cooperation with Allen Institute for Brain Science
Licensed under the Apache License, Version 2.0 (the "License")

Last constructed under Python 3.7, numpy 1.16.4, pandas 0.24.2 and PyQt 5.12.2
"""

import os
import shutil
import struct
import sys
import threading
import time
import zipfile
from queue import Queue
from urllib import request
import re

import numpy
import pandas
from PyQt5 import QtWidgets, QtCore

__version__ = 4.2
__author__ = "Jure Fabjan"

# Just two experiments to use if checking if it works
ExperimentIDs = 72340131, 74988690

# TODO: load all experiments for mice and humans (=> rows), collect meta-data (sex, age, species, etc. => columns). then: get variance/std by meta-data and brain-region
# how do i get a list of all experiments?
# http://help.brain-map.org/display/api/Allen%2BBrain%2BAtlas%2BAPI
# https://portal.brain-map.org/explore/transcriptome

class Interface(QtWidgets.QMainWindow):
    """ Interface for the programme
    """

    def __init__(self):
        super(Interface, self).__init__()
        self.setGeometry(500, 400, 750, 300)
        self.setWindowTitle("Allen Brain Atlas tool")

        # Initialisation of parameters for the processing.
        self.structureGraphID = {"mouse": 1, "developing mouse": 17}

        self.referenceSpaceID = {"E11pt5 DevMouse 2012": "E11pt5_DevMouse2012_gridAnnotation.zip",
                                 "E13pt5 DevMouse 2012": "E13pt5_DevMouse2012_gridAnnotation.zip",
                                 "E15pt5 DevMouse 2012": "E15pt5_DevMouse2012_gridAnnotation.zip",
                                 "E16pt5 DevMouse 2012": "E16pt5_DevMouse2012_gridAnnotation.zip",
                                 "E18pt5 DevMouse 2012": "E18pt5_DevMouse2012_gridAnnotation.zip",
                                 "P14 DevMouse 2012": "P14_DevMouse2012_gridAnnotation.zip",
                                 "P28 DevMouse 2012": "P28_DevMouse2012_gridAnnotation.zip",
                                 "P4 DevMouse 2012": "P4_DevMouse2012_gridAnnotation.zip",
                                 "P56 DevMouse 2012": "P56_DevMouse2012_gridAnnotation.zip",
                                 "P56 Mouse": "P56_Mouse_gridAnnotation.zip"}

        self.IDs = []

        # Interface elements
        self.lbFileName = QtWidgets.QLabel("Name of the output file:", self)
        self.lbFileName.setGeometry(50, 30,
                                    120, 30)

        self.leFileName = QtWidgets.QLineEdit("ABAtlus", self)
        self.leFileName.setGeometry(170, 30,
                                    200, 30)

        self.lbExperimentID = QtWidgets.QLabel("Set the experiment ID:", self)
        self.lbExperimentID.setGeometry(50, 70,
                                        120, 30)

        self.leExperimentID = QtWidgets.QLineEdit(self)
        self.leExperimentID.setGeometry(170, 70,
                                        100, 30)
        self.leExperimentID.returnPressed.connect(self.run)

        self.btOpenFile = QtWidgets.QPushButton("Open file", self)
        self.btOpenFile.move(280, 70)
        self.btOpenFile.clicked.connect(self.load_ids)

        self.cbStructureGID = QtWidgets.QComboBox(self)
        self.cbStructureGID.setGeometry(170, 110,
                                        150, 30)
        self.cbStructureGID.addItems(sorted(list(self.structureGraphID.keys()))[::-1])

        self.lbStructureGID = QtWidgets.QLabel("Choose structure graph:", self)
        self.lbStructureGID.setGeometry(50, 110,
                                        120, 30)

        self.cbReferenceSID = QtWidgets.QComboBox(self)
        self.cbReferenceSID.setGeometry(170, 150,
                                        150, 30)
        self.cbReferenceSID.addItems(sorted(list(self.referenceSpaceID.keys()))[::-1])

        self.lbReferenceSID = QtWidgets.QLabel("Choose annotation:", self)
        self.lbReferenceSID.setGeometry(50, 150,
                                        120, 30)

        self.btnRun = QtWidgets.QPushButton("Run", self)
        self.btnRun.setGeometry(80, 230,
                                100, 30)
        self.btnRun.clicked.connect(self.run)

        self.btOpenExperiment = QtWidgets.QPushButton("Open Experiment", self)
        self.btOpenExperiment.move(200, 230)
        self.btOpenExperiment.clicked.connect(self.load_experiment)

        self.SaveExperiment = QtWidgets.QCheckBox("Save the experiment", self)
        self.SaveExperiment.setGeometry(320, 230,
                                        120, 30)

        self.lbStatus = QtWidgets.QLabel("Please, set the right parameters and click Run\n" +
                                         "If entering more experiments delimit them by ','.\n" +
                                         "Don't forget to change the name of the output file too!", self)
        self.lbStatus.setGeometry(450, 30,
                                  300, 100)

        self.btnClose = QtWidgets.QPushButton("Close", self)
        self.btnClose.move(625, 260)
        self.btnClose.clicked.connect(self.backback)

        self.show()

        # Additional parameters
        self.experiments_file = False
        self.experiments_file_path = ""
        self.head = False

    def load_ids(self):
        """  Opens a dialog for choosing a file and then opens the .txt file with experiment IDs and
             writes the IDs into leExperimentID.
        """

        file_options = QtWidgets.QFileDialog.Options()
        file_options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose file")
        if file_name != "":
            file = open(file_name, "r").read()
            self.leExperimentID.setText(", ".join(file.split("\n")))

    def load_experiment(self):
        """ Opens a dialog for choosing a file with all settings
        """

        file_options = QtWidgets.QFileDialog.Options()
        file_options |= QtWidgets.QFileDialog.DontUseNativeDialog
        self.experiments_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose file")

        if self.experiments_file_path != "":
            with zipfile.ZipFile(self.experiments_file_path, "r") as file:
                head_path = file.extract("Head.txt")

                with open(head_path, "r") as head_file:
                    self.head = eval(head_file.read())
                    self.leExperimentID.setText(self.head["expIDs"])
                    self.cbStructureGID.setCurrentIndex(self.cbStructureGID.findText(self.head["strgraph"],
                                                                                    QtCore.Qt.MatchFixedString))
                    self.cbReferenceSID.setCurrentIndex(self.cbReferenceSID.findText(self.head["annot"],
                                                                                    QtCore.Qt.MatchFixedString))

    def run(self):
        """ Initialisation of the experiment.  All the parameters must be set before that.
        """

        if self.leExperimentID.text():
            self.IDs = list(map(str.strip, self.leExperimentID.text().split(",")))
            RunAnalysis()

        else:
            self.lbStatus.setText("The experiment ID is missing. Please enter a valid ID.")

    def update_status(self, number):
        """ Updates the status of analysis on the interface.
        """

        statuses = ["Experiment is starting. Current status:\n\t- Downloading annotation",
                    "{previous}\tDONE\n\t- Downloading ontology",
                    "{previous}\tDONE\n\t- Downloading experiment data",
                    "{previous}\tDONE\n\t- Saving experiment data",
                    "{previous}\tDONE\n\t- Processing data",
                    "{previous}\tDONE\n\t- Writing to file",
                    "{previous}\tDONE\n\nProcessing finished.\nPlease set new parameters and click Run",
                    "{previous}\tDONE\n\tProcess aborted.",
                    "Experiment is starting. Current status:\n\t- Downloading ontology",
                    "{previous}\tDONE\n\t- Downloading annotation"]
        previous = self.lbStatus.text()
        self.lbStatus.setText(statuses[number].format(previous=previous))

        App.processEvents()

    def backback(self):
        """ Manages the closing of the aplication.
        """
        self.close()


class RunAnalysis:
    """ Manages the analysis pipeline.  Does communicate directly with Interface in the process.
    """
    def __init__(self):
        self.used_ontology = None
        self.ontology_copy = None
        self.used_annotation = None
        self.threading_data = None
        self.grids = []
        self.first_analysis()

        self.q = None
        self.t = None

    def download_new(self):
        """ Downloads the data, used in the experiment. 
        """

        self.q = Queue()

        GUI.update_status(0)
        self.used_annotation = Annotation(GUI.referenceSpaceID[GUI.cbReferenceSID.currentText()])

        self.threading_data = list(zip(["ontology"] + ["grid"] * len(GUI.IDs),
                                       [GUI.structureGraphID[GUI.cbStructureGID.currentText()]] + GUI.IDs,
                                       [0] + list(range(len(GUI.IDs)))))
        self.grids = [None for _ in self.threading_data[1:]]

        for _ in self.threading_data:
            self.t = threading.Thread(target=self.download_threader)
            self.t.daemon = True
            self.t.start()

        for worker in range(len(self.threading_data)):
            self.q.put(worker)

        self.q.join()

        GUI.update_status(2)

        if GUI.SaveExperiment.isChecked():
            GUI.update_status(3)
            self.save_experiment()

    def download_threader(self):
        """" Initiates the threads.
        """
        while True:
            worker = self.q.get()
            self.download(worker)
            self.q.task_done()

    def download(self, threading_id):

        data_type, grid_id, i = self.threading_data[threading_id]
        if data_type == "ontology":
            GUI.update_status(1)
            self.used_ontology = Ontology(grid_id)
            self.ontology_copy = self.used_ontology.Array.copy()
        elif data_type == "grid":
            self.grids[i] = Grid(grid_id, i, self.used_annotation.Array)

    def import_old(self):
        """ Import preexisting data
        """

        initial_path = os.getcwd()
        with zipfile.ZipFile(GUI.experiments_file_path, "r") as experiments_file:
            if "temporary_data" in os.listdir(os.getcwd()):
                shutil.rmtree(os.path.join(initial_path, "temporary_data"))
            experiments_file.extractall(path=os.path.join(initial_path, "temporary_data"))
            os.chdir("temporary_data")

            GUI.update_status(8)
            ontology_array = pandas.read_csv("Ontology.csv")
            self.used_ontology = Ontology(GUI.structureGraphID[GUI.cbStructureGID.currentText()],
                                          ontology_array)

            GUI.update_status(9)
            with open("Annotation.txt", "r") as file:
                self.used_annotation = Annotation(GUI.referenceSpaceID[GUI.cbReferenceSID.currentText()],
                                                  numpy.array(eval(file.read())))

            GUI.update_status(2)
            self.grids = []
            for i, ID in enumerate(GUI.IDs):
                with open(f"Grid{i}.txt", "r") as file:
                    self.grids.append(Grid(ID,
                                           i,
                                           numpy.array(eval(file.read()))))

            os.chdir("..")
            shutil.rmtree(os.path.join(initial_path, "temporary_data"))

        if GUI.SaveExperiment.isChecked():
            GUI.update_status(3)
            self.save_experiment()

    def first_analysis(self):
        """ Analysis of single experiments.  Also communicates to Interface to change the status.
        """

        if GUI.experiments_file:
            self.import_old()

        else:
            self.download_new()

        # Checking the names of the experiments.  The user has the ability to change them.
        name_check = NameCheck([(gr.ID, gr.name) for gr in self.grids])
        if name_check.checked:
            for grid, name in zip(self.grids, name_check.names):
                grid.name = name
            name_check.close()

            GUI.update_status(4)
            for i, grid in enumerate(self.grids):
                self.used_ontology.exp_value_structures(grid.Array, i)

            GUI.update_status(5)
            wish_list = ["name", "mean{}", "min{}", "max{}", "volume{}", "sum{}"]
            try:
                self.writer(wish_list, self.used_ontology, self.grids)
            except Exception as e:
                print(e)

            GUI.update_status(6)

        else:
            GUI.update_status(7)
            name_check.close()

    def save_experiment(self):
        """ Saves the experiment data into a file
        """
        GUI.leFileName.text()
        initial_path = os.getcwd()
        if "temporary_data" in os.listdir(os.getcwd()):
            shutil.rmtree(os.path.join(initial_path, "temporary_data"))
        os.makedirs(os.path.join(initial_path, "temporary_data"))
        os.chdir("temporary_data")
        file_names = ["Head.txt",
                      "Ontology.csv",
                      "Annotation.txt"]
        with open(file_names[0], "w") as file:
            head = {"expIDs": ", ".join(GUI.IDs),
                    "strgraph": GUI.cbStructureGID.currentText(),
                    "annot": GUI.cbReferenceSID.currentText(),
                    "expNames": {grid.ID: grid.name for grid in self.grids}}

            file.write(str(head))

        self.ontology_copy.to_csv(file_names[1])

        with open(file_names[2], "w") as file:
            file.write(str(self.used_annotation.Array.tolist()))

        for i, grid in enumerate(self.grids):
            with open(f"Grid{i}.txt", "w") as file:
                file.write(str(grid.Array.tolist()))

        with zipfile.ZipFile(os.path.join(initial_path, GUI.leFileName.text()+".zip"), mode="w") as file:
            for file_name in os.listdir(os.getcwd()):
                file.write(file_name)

        os.chdir("..")
        shutil.rmtree(os.path.join(initial_path, "temporary_data"))

    @staticmethod
    def writer(wish_list, used_ontology, grids):
        """ Writes data from ontology to .xlsx file.
        """

        wish_list += [f"level_{x}" for x in range(used_ontology.MaxDepth - 1, 0, -1)]
        # pylint issue. workaround according to https://stackoverflow.com/questions/59983765/pandas-abstract-class-excelwriter-with-abstract-methods-instantiatedpylint-p
        file = pandas.ExcelWriter(f"{GUI.leFileName.text()}.xlsx") # pylint: disable=abstract-class-instantiated
        for i, grid in enumerate(grids):
            used_ontology.Array[[column.format(i) for column in wish_list]].rename(columns={f"min{i}": "min",
                                                                                            f"max{i}": "max",
                                                                                            f"mean{i}": "mean",
                                                                                            f"sum{i}": "sum",
                                                                                            f"volume{i}": "volume"}).to_excel(file, grid.name)

        file.save()


class NameCheck(QtWidgets.QWidget):
    """ Asks if the names of the experiments are correct.
        Argument is a list of IDs and corresponding names.
    """

    def __init__(self, names):
        super(NameCheck, self).__init__()
        self.checked = False

        QtWidgets.QLabel("ID", self).move(70, 10)
        QtWidgets.QLabel("Name", self).move(135, 10)

        # Makes a line edit for every experiment name and writes the name inside
        self.leNames = []
        for i, (ID, name) in enumerate(names):
            QtWidgets.QLabel(ID, self).setGeometry(50, 40 * (i + 1),
                                                   50, 30)
            self.leNames.append(QtWidgets.QLineEdit(name, self))
            self.leNames[-1].setGeometry(100, 40 * (i + 1),
                                         100, 30)

        i = len(names) - 1
        self.lbText = QtWidgets.QLabel("Confirm the names.", self)
        self.lbText.setGeometry(50, 40 * (i + 2),
                                150, 30)

        self.btYes = QtWidgets.QPushButton("Yes", self)
        self.btYes.move(230, 40 * (i + 2))
        self.btYes.clicked.connect(self.yes)

        self.btNo = QtWidgets.QPushButton("Cancel", self)
        self.btNo.move(330, 40 * (i + 2))
        self.btNo.clicked.connect(self.close)

        self.setGeometry(625, 300,
                         500, 40 * (i + 4))
        self.setWindowTitle("Name check")

        self.show()

        # A loop that stops the whole program until the user clicks Yes, Cancel or Close.
        while not self.checked:
            App.processEvents()
            time.sleep(0.05)

        self.names = list(map(QtWidgets.QLineEdit.text, self.leNames))

    def yes(self):
        """ Method that runs when Yes Push Button is clicked.
        """

        self.checked = True


class Ontology:
    """ Ontology management inside the program.
    """

    def __init__(self, ont_id, data=pandas.DataFrame(), max_depth=0):

        self.url = "http://api.brain-map.org/api/v2/data/query.csv?" + \
                   "criteria=model::Structure," + \
                   f"rma::criteria,[ontology_id$eq{ont_id}]," + \
                   "rma::options[order$eq%27structures.graph_order%27][num_rows$eqall]"
        self.Array = data
        self.MaxDepth = max_depth

        if not max_depth:
            self.download_ontology()

    def download_ontology(self):
        """ Downloads the ontology from online source.
        """

        # Download and read the source file, keep only selected columns and set 'id' as the index provider
        self.Array = pandas.read_csv(request.urlretrieve(self.url)[0])[["id", "atlas_id", "name", "acronym", "parent_structure_id", "depth", "structure_id_path"]].set_index("id")

        self.Array["containing_ids"] = self.Array.index.map(lambda x: self.Array.loc[self.Array.structure_id_path.str.contains(f"/{x}/", regex=False)].index).to_series(index=self.Array.index).map(list)

        self.MaxDepth = max(self.Array.structure_id_path.apply(lambda x: len(x.split("/")) - 2))

        # Split the id_path (get str IDs in separate columns) => rename column names => replace IDs with names (index is an int, so we create a new series from names and indices converted to str) => concatenate with existing array
        self.Array = pandas.concat([self.Array, self.Array.structure_id_path.str.split("/", expand=True).iloc[:, 1:-1].rename(columns={i: f"level_{self.MaxDepth - i}" for i in range(1, self.MaxDepth+1)}).replace(pandas.Series(self.Array.name.values, index=self.Array.index.astype(str)))], join="outer", axis=1)

    def exp_value_structures(self, data, n):
        """ Computation of wanted tests on the data.
        """

        # Minimum value, maximum value , sum and number of instances in every structure
        # Note that mean != sum / volume as volume also counts non-recorded voxels in the experiment (with value -1.0)
        #   while mean just uses the voxels with data acquired
        for new_column in [f"min{n}", f"max{n}", f"sum{n}", f"volume{n}", f"mean{n}"]:
            self.Array[new_column] = 0.0

        relevant_data = self.Array.containing_ids.map(lambda x: data[0, numpy.in1d(data[1, :], x)])
        relevant_data = relevant_data[relevant_data.str.len() != 0]
        self.Array.loc[relevant_data.index, f"volume{n}"] = relevant_data.apply(numpy.size)
        relevant_data = relevant_data.apply(lambda x: numpy.delete(x, numpy.where(x == -1.0)))
        relevant_data = relevant_data[relevant_data.str.len() != 0]
        self.Array.loc[relevant_data.index, f"max{n}"] = relevant_data.apply(numpy.amax)
        self.Array.loc[relevant_data.index, f"min{n}"] = relevant_data.apply(numpy.amin)
        self.Array.loc[relevant_data.index, f"sum{n}"] = relevant_data.apply(numpy.sum)
        self.Array.loc[relevant_data.index, f"mean{n}"] = relevant_data.apply(numpy.mean)


class Annotation:
    """ Annotation management inside the program.
    """

    def __init__(self, space_id, array=()):

        self.url = f"http://download.alleninstitute.org/informatics-archive/current-release/mouse_annotation/{space_id}"

        if type(array) != tuple:
            self.Array = numpy.array(array)
        else:
            self.Array = self.download()

    def download(self):
        """ Downloads the annotation from an online source.
        """

        return numpy.array(list(struct.iter_unpack("<I", zipfile.ZipFile(request.urlretrieve(self.url)[0]).read("gridAnnotation.raw")))).flatten()


class Grid:
    """ Data management inside the program.
    """

    def __init__(self, set_id, index, used_annotation, array=False, name=""):

        self.name = name
        self.ID = set_id
        self.Url = f"http://api.brain-map.org/grid_data/download/{self.ID}?include=energy"
        self.Index = index
        self.UsedAnnotation = used_annotation

        if name:
            self.rawArray = array
            self.Array = numpy.array([array, self.UsedAnnotation])
            self.Array = self.Array[:, self.Array[1] != 0]

        else:
            self.Array = self.download()

    def download(self):
        """ Downloads the data from an online source.
        """

        master_file = zipfile.ZipFile(request.urlretrieve(self.Url)[0])
        with master_file.open("data_set.xml") as data:
            # TODO: better parse as xml and use xquery
            self.name = re.search("<path>\\S*", data.read().decode("utf-8"))[0].split("/")[-2].split(".")[0].split("_")[0]

        return numpy.array([numpy.array(list(struct.iter_unpack("<f", master_file.read("energy.raw")))).flatten(), self.UsedAnnotation])


if __name__ == "__main__":
    lock = threading.Lock()

    App = QtWidgets.QApplication(sys.argv)
    GUI = Interface()
    App.exec_()