$('#switchInput[type=checkbox]').on('click', function(){
    var chkValue = $('#switchInput[type=checkbox]:checked').val();
    var enableToggle = $('#enable_tog');

    if (enableToggle.length === 0) {
        var showAvailableOnly = chkValue === 'on';

        $('#all_tog .build-floor-container').each(function () {
            var floor = $(this);
            var cards = floor.find('.lectureinfo-box');

            cards.each(function () {
                var card = $(this);
                var isAvailableClassroom = card.find('.lecturecon.poss').length > 0;
                card.toggle(!showAvailableOnly || isAvailableClassroom);
            });

            var hasAvailableClassroom = cards.filter(function () {
                return $(this).find('.lecturecon.poss').length > 0;
            }).length > 0;

            floor.toggle(!showAvailableOnly || hasAvailableClassroom);
        });
        return;
    }

    if (chkValue == 'on') {
        enableToggle.css('display', 'flex');
        $('#all_tog').css('display', 'none');
    }
    else {
        enableToggle.css('display', 'none');
        $('#all_tog').css('display', 'flex');
    }
})
