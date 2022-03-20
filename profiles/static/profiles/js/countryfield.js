// get the value of the country field when the page loads and store it in a variable.
// value will be an empty string if the first option is selected.
// to determine if that's selected use this as a boolean.
// So if country selected is false. Then the colour of this element will be the grey placeholder colour.
// capture the change event.
// every time the box changes get the value of it.
// then determine the proper colour.

let countrySelected = $('#id_default_country').val();
if(!countrySelected) {
    $('#id_default_country').css('color', '#aab7c4');
};
$('#id_default_country').change(function() {
    countrySelected = $(this).val();
    if(!countrySelected) {
        $(this).css('color', '#aab7c4');
    } else {
        $(this).css('color', '#000');
    }
});