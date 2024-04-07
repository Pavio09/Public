import os
import pandas as pd
import pdfplumber
from PyPDF2 import PdfFileWriter, PdfFileReader
import re
from shutil import copyfile


TAX = 21

class ConvertValues:
    @staticmethod
    def make_float_value_from_string(string_number):
        return round(float(string_number.replace(",", ".")), 2)

    @staticmethod
    def make_string_value_with_comma(float_number):
        return str(float_number).replace(".", ",")

    @staticmethod
    def make_float_vat_value_from_list(data_from_pdf):
        list_split = data_from_pdf.split(" ")

        if "." in list_split[3]:
            value_to_vat = float(list_split[3])
            vat_result = float(list_split[4])
        elif "." in list_split[4]:
            value_to_vat = float(list_split[3] + list_split[4])
            try_vat = round(float(value_to_vat) * (TAX / 100), 2)
            vat_result = list_split[5] if len(f"{try_vat:.2f}") <= 6 else list_split[5] + list_split[6]

        str_netto = ConvertValues.make_string_value_with_comma(value_to_vat)
        str_vat = ConvertValues.make_string_value_with_comma(vat_result)

        return str_netto, str_vat


class SelectNumberOfPageResult:
    def __init__(self, file, search_text):
        self.file = file
        self.search_text = search_text

    def select_page_with_result(self):
        selected_page_with_result = 0
        with pdfplumber.open(self.file) as pdf:
            pages_of_pdf = pdf.pages
            for _ in pages_of_pdf:
                value_text = pdf.pages[selected_page_with_result].extract_text().split("\n")
                if any(re.search(self.search_text, text) for text in value_text):
                    break
                else:
                    selected_page_with_result += 1

        return selected_page_with_result


class SelectPDFWithResult:
    def __init__(self, source, destination, file, iterator):
        self.source = source
        self.destination = destination
        self.file = file
        self.iterator = iterator

    def make_path_file(self):
        source_path = os.path.join(self.source, self.file)
        target_path = os.path.join(self.destination, self.file)

        return source_path, target_path

    def copy_files_between_path(self):
        return copyfile(*self.make_path_file())

    def select_page_pdf_with_result_euro(self, search_text):
        new_name_of_file = f"{self.iterator}.pdf"
        _, target_source = self.make_path_file()
        self.copy_files_between_path()
        numer_of_page_with_result = SelectNumberOfPageResult(target_source, search_text)
        with open(target_source, "rb") as pdf, open(self.destination + new_name_of_file, "wb") as outputpdf:
            page_to_copy_from_source_pdf = PdfFileReader(pdf, strict=False)
            page_to_replace_from_source = PdfFileWriter()
            page_to_replace_from_source.addPage(page_to_copy_from_source_pdf.getPage(
                numer_of_page_with_result.select_page_with_result()))
            page_to_replace_from_source.write(outputpdf)

            return self.destination + new_name_of_file

    def delete_pdf_from_destination_folder(self):
        os.remove(self.make_path_file()[1])


class ManagePDF:
    def __init__(self, selected_page: SelectPDFWithResult, search_text):
        self.selected_file = selected_page.select_page_pdf_with_result_euro(search_text)
        self.search_text = search_text

    def collect_data_from_selected_pdf(self):
        with pdfplumber.open(self.selected_file) as pdf:
            data_list_from_pdf = pdf.pages[0].extract_text().split("\n")

        return data_list_from_pdf

    def collect_gross_and_netto(self):
        data_list_from_pdf = self.collect_data_from_selected_pdf()
        selected_index = next(i for i, v in enumerate(data_list_from_pdf) if re.search(self.search_text, v))
        cost_list = data_list_from_pdf[selected_index]
        comma_netto, comma_vat = ConvertValues.make_float_vat_value_from_list(cost_list)

        return comma_netto, comma_vat

    def title_for_invoice_pdf(self):
        data_list_from_pdf = self.collect_data_from_selected_pdf()
        numer_of_index_nr_invoce = next(i for i, v in enumerate(data_list_from_pdf) if ("N° : ") in v)
        position_symbol_start_number = data_list_from_pdf[numer_of_index_nr_invoce].find(":")
        nr_invoice = data_list_from_pdf[numer_of_index_nr_invoce][(position_symbol_start_number + 2):]

        return nr_invoice

    def date_for_invoice_pdf(self):
        data_list_from_pdf = self.collect_data_from_selected_pdf()
        date_source = data_list_from_pdf[20]
        date = date_source[11:]

        return date

    def collect_all_data_from_pdf(self, country, company, code_vat):
        value_from_invoice = {
            "numer": self.title_for_invoice_pdf(),
            "data": self.date_for_invoice_pdf(),
            "netto": self.collect_gross_and_netto()[0],
            "vat": self.collect_gross_and_netto()[1],
            "kraj": country,
            "firma": company,
            "kod": code_vat
        }

        return value_from_invoice


class CreateExcelWorkBookWithDataFromPDF:
    def __init__(self, data, name_of_file):
        self.data = data
        self.name_of_file = name_of_file

    def create_excel(self):
        nested_dict_from_data = [list(value.values()) for value in self.data]
        columns_name = self.data[0].keys()
        df = pd.DataFrame(nested_dict_from_data, columns=columns_name)
        writer = pd.ExcelWriter(f"{self.name_of_file}.xlsx", engine="xlsxwriter")
        df.to_excel(writer, sheet_name="Raport", index=False)
        writer.save()


if __name__ == "__main__":
    country = "Niemcy"
    dict_country_map = {
        "Niemcy": "Total in Euro",
        "Francja": "Total en Euro",
        "Belgia": "Totaal in Euro",
        "Luxembourg": "Total en Euro"
    }

    source = f"{country}\\"
    destination = "output\\"
    new_dir = os.path.join(destination, f"{country}\\")
    os.makedirs(new_dir, exist_ok=True)
    data = []
    for i, file in enumerate(os.listdir(source), start=1):
        select_pdf = SelectPDFWithResult(source=source, destination=new_dir, file=file, iterator=i)
        manage_pdf = ManagePDF(select_pdf, dict_country_map[country])
        data.append(manage_pdf.collect_all_data_from_pdf(country, "AS24", "1"))
        select_pdf.delete_pdf_from_destination_folder()
    create_excel_file = CreateExcelWorkBookWithDataFromPDF(data, f"{new_dir}//{country}")
    create_excel_file.create_excel()
