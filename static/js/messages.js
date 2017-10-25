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

    $(document).ready(function() {
        displayCorrectMessages();
        updateText();
    });

    $("#next-button").click(function() {
        currentPage = Math.min(currentPage+1, Math.ceil(total/pageSize));
        displayCorrectMessages();
        updateText();
    });

    $("#prev-button").click(function() {
        currentPage = Math.max(currentPage-1, 1);
        displayCorrectMessages();
        updateText();
    });

    $(".modal-delete").click(function() {
        var pk=$(this).parents("tr[id^='message-no-']").find("input[id^='message-pk-']")
                      .attr("id").slice(11);  // slice off "message-pk-" from id to give just the number
        var djangoUrl = $(".modal-body a").attr("href");
        var newUrl = djangoUrl.replace(/[\d+][-\d+]*$/, pk);
        $(".modal-body a").attr("href", newUrl);
        $("#plural").text("this message");
    });

    $("#delete-selected").click(function() {
        var checkedPkString = $("input[id^='message-pk-']:checked").map(function() {
            console.log(this.id.slice(11));
            return this.id.slice(11);
        }).get().join("-");
        var djangoUrl = $(".modal-body a").attr("href");
        var newUrl = djangoUrl.replace(/[\d+][-\d+]*$/, checkedPkString);
        $(".modal-body a").attr("href", newUrl);
        if (checkedPkString.indexOf("-") == -1) {
            $("#plural").text("this message");
        }
        else {
            $("#plural").text("these messages");    
        }        
    });
}
