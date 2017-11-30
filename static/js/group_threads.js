function threadTable(total) {
    var pageSize = 10, currentPage = 1;

    function displayCorrectThreads() {
        for (var i=1; i<=total; i++) {
            if (i<=(currentPage-1)*pageSize || i>currentPage*pageSize) {
                $("#thread-no-"+i).hide();
            }
            else {
                $("#thread-no-"+i).show();
            }
        }
    }

    function updateText() {
        $("#first").text(currentPage);
        $("#total").text(Math.ceil(total/pageSize));
    }

    $(document).ready(function() {
        displayCorrectThreads();
        updateText();
    });

    $("#next-button").click(function() {
        currentPage = Math.min(currentPage+1, Math.ceil(total/pageSize));
        displayCorrectThreads();
        updateText();
    });

    $("#prev-button").click(function() {
        currentPage = Math.max(currentPage-1, 1);
        displayCorrectThreads();
        updateText();
    });
}
