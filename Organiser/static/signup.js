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
        $(div).find("data").val("ok");
    }
    else {
        $(div).removeClass("has-success").addClass("has-error");
        $(div).find(".help-block").removeClass("hide");
        $(div).find(".glyphicon-remove").removeClass("hide");
        $(div).find(".glyphicon-ok").addClass("hide");
        $(div).find("data").val("bad");
    }

};

var check_all_status = function(){
    if ($("data.mail").val() == "ok" && $("data.pass").val() == "ok" && $("data.check").val() == "ok")
        $("button").addClass("btn-success").removeClass("btn-danger").removeAttr("disabled", "disabled");
    else
        $("button").removeClass("btn-success").addClass("btn-danger").attr("disabled", "False");
}

var check_mail = function (){
    $.ajax({
        url: mail_url,
        data: {mail: $(".js-mail").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-mail");
        check_all_status();
    });
};


var check_pass = function (){
    $.ajax({
        url: pass_url,
        data: {pass: $(".js-pass").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-pass");
        check_all_status();
    });
};

var check_repeat = function (){
    $.ajax({
        url: check_url,
        data: {pass: $(".js-pass").val(),
               passcheck: $(".js-check").val(),},
    })
    .done(function( json_obj ) {
        implement_answer(json_obj, ".div-repeat");
        check_all_status();
    });
};