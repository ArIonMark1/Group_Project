window.onload = function () {
    let rating_inputs = document.querySelectorAll('div.review-rating input')
    rating_inputs.forEach(function (input) {
        input.addEventListener('input', function (event) {
            event.target.parentElement.firstElementChild.firstElementChild.innerHTML = `${event.target.value}`;
            let rating_values = document.querySelectorAll('div.review-rating i.rating_num')
            let summ = 0;
            rating_values.forEach(function (value) {
                summ += Number(value.innerHTML)
            })
            document.querySelector('i.rating_sum').innerHTML = `${summ / rating_values.length}`;
        })
    })
}