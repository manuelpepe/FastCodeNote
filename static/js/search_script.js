
$(document).ready(function(){
    /* Defining variables */
    var type_of_search = $("#type_of_search").val(),
        $LangSearch = $('#leng-search'),
        $DescSearch = $('#desc-search'),
        $TitSearch = $('#tit-search');

    function ShowLangForm(){
        $TitSearch.hide("fade", 1000);
        $DescSearch.hide("fade", 1000);
        $LangSearch.delay(1000).show("fade", 1000);
    }

    function ShowTitForm(){
        $LangSearch.hide("fade", 1000);
        $DescSearch.hide("fade", 1000);
        $TitSearch.delay(1000).show("fade", 1000);
    }

    function ShowDescForm(){
        $LangSearch.hide("fade", 1000);
        $TitSearch.hide("fade", 1000);
        $DescSearch.delay(1000).show("fade", 1000)
    }


    /* This will update the form */
    function UpdateContent(type){
        if (type === 'title') {
            ShowTitForm()
        } else if(type === 'lang'){
            ShowLangForm();
        } else if(type === 'desc'){
            ShowDescForm()
        } else {
            return 'Typeofsearch Error'
        }
    }

    /* This will change the form when the select field is changed */
    $("#type_of_search").on('change', function(){
        type_of_search = $(this).val()
        UpdateContent(type_of_search)
    })
});