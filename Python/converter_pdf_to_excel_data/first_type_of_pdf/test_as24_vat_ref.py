from converter_pdf_to_excel_data.first_type_of_pdf.invoce_as24 import ConvertValues, ManagePDF, SelectNumerOfPageResult, SelectPDFWithResult

sample_file = "AS24_15.02.2022.pdf"
source = ""
destination = ""
path_to_correct_pdf = ""


def test_selected_numer_of_result_from_pdf():
    selected_numer_of_result = SelectNumerOfPageResult(path_to_correct_pdf, "Totaal in Euro")
    assert selected_numer_of_result.select_page_with_result() == 1


def test_make_init_value_positive():
    assert ConvertValues.make_float_value_from_string("1,2") == 1.2


def test_make_init_value_negative():
    assert ConvertValues.make_float_value_from_string("1,2") != 1.2


def test_make_from_integer_string():
    assert ConvertValues.make_string_value_with_comma(1.2) == "1,2"


def test_select_page_from_composite():
    select_pdf = SelectPDFWithResult(source, destination, sample_file, 1)
    pdf_to_select = ManagePDF(select_pdf, "Totaal in Euro")
    assert pdf_to_select.selected_file == destination + "1.pdf"


def test_gross_and_netto_value_from_pdf_positive():
    select_pdf = SelectPDFWithResult(source, destination, sample_file, 1)
    pdf_to_select = ManagePDF(select_pdf, "Totaal in Euro")
    assert pdf_to_select.collect_gross_and_netto() == ("31454,92", "6605,54")


def test_gross_and_netto_value_from_pdf_negative():
    select_pdf = SelectPDFWithResult(source, destination, sample_file, 1)
    pdf_to_select = ManagePDF(select_pdf, "Totaal in Euro")
    assert pdf_to_select.collect_gross_and_netto() != ("31454,00", "6605,54")
