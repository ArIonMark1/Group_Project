ymaps.ready(init);


let check_was_done = false;



function onNewAd(event) {
    if (check_was_done) {
        check_was_done = false;
        return;
    }
    event.preventDefault();
    const address = $('#address').val();

    if (!address) {
        showError('Address must not be empty');
        return;
    }

    checkAddress(address)
        .then(result => {
            if (result.error) {
                showError(result.error);
                return;
            }
            check_was_done = true;
            $(event.srcElement).trigger('click');
        }, err => {
            showError('Internal server error');
        })
}

function onFileUpload(event) {
    const uploadedFiles = $('#uploaded-files');
    uploadedFiles.empty();
    const fileList = event.target.files;
    for (let i = 0; i < fileList.length; i++) {
        const { name: fileName, size } = fileList[i];
        const fileSize = (size / 1000).toFixed(2);

        const src = URL.createObjectURL(fileList[i]);

        const img = $('<img class="preview-img"></img>');
        img.attr('src', src);

        const container = $('<div class="preview-img-container"/>');
        const description = $('<span/>');
        description.text(`${fileName} - ${fileSize}KB`);
        container.append(img);
        container.append(description);

        uploadedFiles.append(container);
    }
}

function onAmenitySelected(event) {
    let div = $(event.target);
    while (!div.hasClass('amenity-clickable')) {
        div = div.parent();
    }

    const convid = div.attr('convid');
    if (!convid) {
        return;
    }
    const prevValue = $('#id_selected_amenities').val();
    const currentAmenities = prevValue ? prevValue.split(',') : [];
    if (div.attr('selected')) {
        div.removeAttr('selected');
        div.children().css({ 'color': 'var(--black_40)', 'font-weight': 'normal' });
        const index = currentAmenities.indexOf(convid);
        if (index > -1) { // only splice array when item is found
            currentAmenities.splice(index, 1); // 2nd parameter means remove one item only
        }
    } else {
        div.attr('selected', true);
        div.children().css({ 'color': 'black', 'font-weight': 'bolder' });
        currentAmenities.push(convid);
    }
    $('#id_selected_amenities').val(currentAmenities.join(','));
}

function showError(message) {
    $('#address-notice').text(message);
    $('#address').addClass('input_error');
    $('#address-notice').css('display', 'block');
}

function clearAddressErrors() {
    $('#address').removeClass('input_error');
    $('#address-notice').css('display', 'none');
}

function init() {


    $(document).ready(function () {
        $('#id_image').attr("multiple", "true");
    });

    var suggestView = new ymaps.SuggestView('address');
    $('#address').change(() => clearAddressErrors());
    suggestView.events.add(
        'select',
        e => checkAddress(e.get('item').value)
            .then(result => showResult(result.obj))
    );

    var myPlacemark,
        myMap = new ymaps.Map('map', {
            center: [55.753994, 37.622093],
            zoom: 9
        }, {
            searchControlProvider: 'yandex#search'
        });

    var location = ymaps.geolocation.get();
    location.then(
        result => {
            const coords = result.geoObjects.position;
            myMap.setCenter(coords);
            getAddress(coords);
        }
    );

    // Слушаем клик на карте.
    myMap.events.add('click', function (e) {
        var coords = e.get('coords');
        getPlacemark(coords);
        getAddress(coords);
    });

    // Создание метки.
    function createPlacemark(coords) {
        return new ymaps.Placemark(coords, {
            iconCaption: 'поиск...'
        }, {
            preset: 'islands#violetDotIconWithCaption',
            draggable: true
        });
    }

    // Определяем адрес по координатам (обратное геокодирование).
    function getAddress(coords) {
        getPlacemark(coords).properties.set('iconCaption', 'поиск...');
        ymaps.geocode(coords).then(function (res) {
            var firstGeoObject = res.geoObjects.get(0);
            setPlacemarkText(firstGeoObject);
            $('#address').val(firstGeoObject.getAddressLine());
        });
    }

    function showResult(obj) {
        // Удаляем сообщение об ошибке, если найденный адрес совпадает с поисковым запросом.
        clearAddressErrors();

        var mapContainer = $('#map'),
            bounds = obj.properties.get('boundedBy'),
            // Рассчитываем видимую область для текущего положения пользователя.
            mapState = ymaps.util.bounds.getCenterAndZoom(
                bounds,
                [mapContainer.width(), mapContainer.height()]
            ),
            // Сохраняем полный адрес для сообщения под картой.
            address = [obj.getCountry(), obj.getAddressLine()].join(', '),
            // Сохраняем укороченный адрес для подписи метки.
            shortAddress = [obj.getThoroughfare(), obj.getPremiseNumber(), obj.getPremise()].join(' ');
        // Убираем контролы с карты.
        mapState.controls = [];
        // Создаём карту.
        myMap.setCenter(mapState.center, mapState.zoom);
        myPlacemark = getPlacemark(mapState.center);
        setPlacemarkText(obj);
    }

    function setPlacemarkText(firstGeoObject) {
        myPlacemark.properties
            .set({
                // Формируем строку с данными об объекте.
                iconCaption: [
                    // Название населенного пункта или вышестоящее административно-территориальное образование.
                    firstGeoObject.getLocalities().length ? firstGeoObject.getLocalities() : firstGeoObject.getAdministrativeAreas(),
                    // Получаем путь до топонима, если метод вернул null, запрашиваем наименование здания.
                    firstGeoObject.getThoroughfare() || firstGeoObject.getPremise()
                ].filter(Boolean).join(', '),
                // В качестве контента балуна задаем строку с адресом объекта.
                balloonContent: firstGeoObject.getAddressLine()
            });
    }

    function getPlacemark(coords) {

        if (myPlacemark) {
            myPlacemark.geometry.setCoordinates(coords);
        }
        else {
            myPlacemark = createPlacemark(coords);
            myMap.geoObjects.add(myPlacemark);
            // Слушаем событие окончания перетаскивания на метке.
            myPlacemark.events.add('dragend', function () {
                getAddress(myPlacemark.geometry.getCoordinates());
            });
        }
        return myPlacemark;
    }

}

function checkAddress(address) {
    return ymaps.geocode(address).then(function (res) {
        var obj = res.geoObjects.get(0),
            error, hint;

        if (obj) {
            // Об оценке точности ответа геокодера можно прочитать тут: https://tech.yandex.ru/maps/doc/geocoder/desc/reference/precision-docpage/
            switch (obj.properties.get('metaDataProperty.GeocoderMetaData.precision')) {
                case 'exact':
                    break;
                case 'number':
                case 'near':
                case 'range':
                    error = 'Неточный адрес, требуется уточнение';
                    hint = 'Уточните номер дома';
                    break;
                case 'street':
                    error = 'Неполный адрес, требуется уточнение';
                    hint = 'Уточните номер дома';
                    break;
                case 'other':
                default:
                    error = 'Неточный адрес, требуется уточнение';
                    hint = 'Уточните адрес';
            }
        } else {
            error = 'Адрес не найден';
            hint = 'Уточните адрес';
        }

        // Если геокодер возвращает пустой массив или неточный результат, то показываем ошибку.
        return {
            obj: obj,
            error: error,
            hint: hint
        };
    });
}