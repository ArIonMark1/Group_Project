window.onload = function () {
    var seats = document.querySelector('.select-seats')
    var periods = document.querySelector('.form-peoples')
    var confirm_btn = document.querySelector('.date-btn')
    var start_date = document.querySelector('input[id=start_date]')
    var end_date = document.querySelector('input[id=end_date]')

    start_date.addEventListener('change', function (event) {
            document.querySelector('.date-btn').classList.add('hidden');
            RenderSeats(start_date.value, end_date.value, seats.value);
        });
    end_date.addEventListener('change', function (event) {
            document.querySelector('.date-btn').classList.add('hidden');
            RenderSeats(start_date.value, end_date.value, seats.value);
        });
    seats.addEventListener('change', function (event) {
            document.querySelector('.date-btn').classList.add('hidden');
            RenderSeats(start_date.value, end_date.value, seats.value);
    });


    function RenderSeats(start_date, end_date, seats) {
        console.log(start_date, end_date, seats)
        if(start_date && end_date && seats) {

            periods.classList.remove('hidden');
            $.ajax({
            url: window.location.pathname + start_date + "/" + end_date + "/" + seats + "/",

            success: function (data) {
                $('.form-peoples').html(data.result);
                $(document).ready(function() {
                $('select.period-select').on('change', function(event){
                    var dates = event.target.selectedOptions[0].innerText;
                    if (isNaN(dates)) {
                        var selected_dates = dates.matchAll(/\d{2}\/\d{2}\/\d\d\d\d/g);
                        selected_dates = Array.from(selected_dates)
                        var date_from = selected_dates[0][0].split('/').reverse().join('-');
                        var date_to = selected_dates[1][0].split('/').reverse().join('-');
                        document.querySelector('input[id=start_date]').value = date_from;
                        document.querySelector('input[id=end_date]').value = date_to;
                        $.ajax({
                        url: window.location.pathname + date_from + "/" + date_to + "/" + seats + "/",

                        success: function (data) {
                            $('.form-peoples').html(data.result);
                            $(document).ready(function () {
                             $('select.period-select').on('change', function(event){
                                document.querySelector('.date-btn').classList.remove('hidden');
                             })
                            })
                            }

                        })
                    }
                    else{
                        document.querySelector('.date-btn').classList.remove('hidden');
                    }

                });
            });
            },
        });
        }
    }

}
