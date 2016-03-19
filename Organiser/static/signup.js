
$(document).ready(function() {
    $(".js-mail").on('input', check_mail);
    $(".js-pass").on('input', check_pass);
    $(".js-check").on('input', check_repeat);
});

var implement_answer = function(json_obj, div){
    if (json_obj.answer) {
        $(div).removeClass("has-error").addClass("has-success");
        $(div).find(".help-block").addClass("hide");
        $(div).find(".glyphicon-remove").addClass("hide");
        $(div).find(".glyphicon-ok").removeClass("hide");
    }
    else {
        $(div).removeClass("has-success").addClass("has-error");
        $(div).find(".help-block").removeClass("hide");
        $(div).find(".glyphicon-remove").removeClass("hide");
        $(div).find(".glyphicon-ok").addClass("hide");
    }
};

var check_mail = function (){
    $.ajax({
        url: mail_url,
        data: {mail: $(".js-mail").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-mail");
    });
};


var check_pass = function (){
    $.ajax({
        url: pass_url,
        data: {pass: $(".js-pass").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-pass");
    });
    $(".js-check").trigger("change");
};

var check_repeat = function (){
    $.ajax({
        url: check_url,
        data: {pass: $(".js-pass").val(),
               passcheck: $(".js-check").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-repeat");
    });
};