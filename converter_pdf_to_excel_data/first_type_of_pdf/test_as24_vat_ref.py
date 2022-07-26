from ClassAS24 import ConvertValues, ManagePDF, SelectNumerOfPageResult, SelectPDFWithResult

sample_file = 'AS24_15.02.2022.pdf'
source = ""
destination = ""
path_to_correct_pdf = ""

def test_selected_numer_of_result_from_pdf(path_to_correct_pdf: str):
    selected_numer_of_result = SelectNumerOfPageResult(file=path_to_correct_pdf, search_text='Totaal in Euro')
    assert 1 == selected_numer_of_result.select_page_with_result()

def test_make_init_value_positive():
    assert 1.2 == ConvertValues.make_float_value_from_string('1,2')

def test_make_init_value_negative():
    assert '1.2' != ConvertValues.make_float_value_from_string('1,2')

def test_make_from_integer_string():
    assert '1,2' == ConvertValues.make_string_value_with_comma(float(1.2))

def test_select_page_from_composite():
    select_pdf = SelectPDFWithResult(source=source,
                                    destination=destination,
                                    file=sample_file,
                                    iterator=1
                                )
    pdf_to_select = ManagePDF(select_pdf, 'Totaal in Euro')
    assert pdf_to_select.selected_file == destination+'Zmiana 1.pdf'

def test_gross_and_netto_value_from_pdf_positive():
    select_pdf = SelectPDFWithResult(source=source,
                                    destination=destination,
                                    file=sample_file,
                                    iterator=1
                                )
    pdf_to_select = ManagePDF(select_pdf, 'Totaal in Euro')
    assert pdf_to_select.collect_gross_and_netto() == ('31454,92','6605,54')

def test_gross_and_netto_value_from_pdf_negative():
    select_pdf = SelectPDFWithResult(source=source,
                                    destination=destination,
                                    file=sample_file,
                                    iterator=1
                                )
    pdf_to_select = ManagePDF(select_pdf, 'Totaal in Euro')
    assert pdf_to_select.collect_gross_and_netto() != ('31454,00','6605,54')


