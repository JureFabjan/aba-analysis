# from: https://stackoverflow.com/questions/17326973/is-there-a-way-to-auto-adjust-excel-column-widths-with-pandas-excelwriter

from styleframe import StyleFrame
import Utils
# https://stackoverflow.com/questions/42499656/pass-all-arguments-of-a-function-to-another-function
def to_excel(data, filename, **kwargs): #**kwargs passes all keyword arguments to the to_excel-function
    excel_writer = StyleFrame.ExcelWriter(filename)
    sf = StyleFrame(data)
    sf.to_excel(
        excel_writer=excel_writer, 
        best_fit=[n for n in data.index.names], # range(0,len(data.columns.to_list())-1),#list(Utils.getAlphabeticalRange('A', chr(ord('A') + len(data.columns.to_list())))),
        row_to_add_filters=0,
        index=True,
        **kwargs
    )

    excel_writer.save()