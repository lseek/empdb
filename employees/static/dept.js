function no_query() {
    return (!Boolean($("#first_name").val()) &&
            !Boolean($("#last_name").val()) && 
            !Boolean($("#gender").val()) &&
            !Boolean($("#hire_date").val()) &&
            !Boolean($("#curr_title").val()));
}


function hide_search_form_if_empty() {
    if (no_query()) {
        $(".can-hide").hide();
    }
}


function clear_search(evt) {
    if (no_query()) {
        // nothing to "reset" so no need to submit form
        $(".can-hide").hide();
        evt.preventDefault();
    }
    $(".search-fields").val("");
}


function show_search_form(evt) {
    if (no_query()) {
        // form is to be shown - no need to actually submit it.
        form_elems = $(".can-hide");
        form_elems.show();
        evt.preventDefault();
    }
    // else form would already be visible so perform default actions.
}


function init_dept_page() {
    hide_search_form_if_empty();
    // ... because onClick doesn't seem to pass the event object to the handler
    $("#search_btn").on("click", show_search_form);
    $("#clear_search_btn").on("click", clear_search);
}
