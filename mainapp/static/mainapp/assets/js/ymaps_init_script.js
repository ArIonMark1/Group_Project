var myMap;

ymaps.ready(init);

function init() {

  var address = new ymaps.SuggestView(
    'suggest',
    {provider: provider}
  );

};

var provider = {
  suggest :  function(request, options) {
    var resultArray = [];
    var suggest = new ymaps.suggest(request);
    var result = suggest.then( items => {
      for (const i of items) {
        resultArray.push({
          value: i.value.split(',').pop().replace(/\s+/g, ''),
          displayName: i.displayName.split(',').slice(0,2)
        });
      }

      return ymaps.vow.resolve(resultArray);
    });
        return ymaps.vow.resolve(result);
  }
};