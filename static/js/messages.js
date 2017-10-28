function messageBox(total) {
    var pageSize = 10, currentPage = 1;

    function displayCorrectMessages() {
        for (var i=1; i<=total; i++) {
            if (i<=(currentPage-1)*pageSize || i>currentPage*pageSize) {
                $("#message-no-"+i).hide();
            }
            else {
                $("#message-no-"+i).show();
            }
        }
    }

    function updateText() {
        $("#first").text(currentPage);
        $("#total").text(Math.ceil(total/pageSize));
    }

    function checkAbleToDelete() {
        var someChecked = false;
        for (var i=pageSize*(currentPage-1)+1; i<=Math.min(pageSize*currentPage, total); i++) {
            var idString = "tr#message-no-"+i;
            if ($(idString).find("input[type='checkbox'][id^='message-pk-']")
                           .is(":checked")) {
                someChecked = true;
                break;
            }
        }
        if (someChecked) {
            $("#delete-selected").prop("disabled", false);
        }
        else {
            $("#delete-selected").prop("disabled", true);
        }        
    }

    $(document).ready(function() {
        displayCorrectMessages();
        updateText();
    });

    $("#next-button").click(function() {
        currentPage = Math.min(currentPage+1, Math.ceil(total/pageSize));
        displayCorrectMessages();
        updateText();
        checkAbleToDelete();
    });

    $("#prev-button").click(function() {
        currentPage = Math.max(currentPage-1, 1);
        displayCorrectMessages();
        updateText();
        checkAbleToDelete();
    });

    $(".modal-delete").click(function() {
        var pk=$(this).parents("tr[id^='message-no-']").find("input[id^='message-pk-']")
                      .attr("id").slice(11);  // slice off "message-pk-" from id to give just the number
        var djangoUrl = $(".modal-body a").attr("href");
        var newUrl = djangoUrl.replace(/(\d+)(-\d+)*\/$/, pk+"/");
        $(".modal-body a").attr("href", newUrl);
        $("#plural").text("this message");
    });

    $("#delete-selected").click(function() {
        var checkedPkString = $("input[id^='message-pk-']:checked").map(function() {
            var messageNo = $(this).parents("tr[id^=message-no-]").attr("id").slice(11);
            if (messageNo>(currentPage-1)*pageSize && messageNo<=currentPage*pageSize) {
                return this.id.slice(11);
            }
            else {
                return "";
            }
        }).get().filter(function(str) {return str.length>0;}).join("-");
        var djangoUrl = $(".modal-body a").attr("href");
        var newUrl = djangoUrl.replace(/(\d+)(-\d+)*\/$/, checkedPkString+"/");
        $(".modal-body a").attr("href", newUrl);
        if (checkedPkString.indexOf("-") == -1) {
            $("#plural").text("the selected message");
        }
        else {
            $("#plural").text("the selected messages");    
        }        
    });

    $("input[type='checkbox'][id^='message-pk-']").click(checkAbleToDelete);
}
