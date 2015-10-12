$(function() {
  // responsive iframe
  // see: http://blog.apps.npr.org/pym.js/
  var child = new pym.Child({id: 'councillor-iframe'});

  // Use parent URL as fb share URL
  function addFacebookShare(d, s, id) {
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) return;
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.3";
      fjs.parentNode.insertBefore(js, fjs);
  }

  function setShareUrl(url) {
    $('.fb-share-button').attr('data-href', url);
    addFacebookShare(document, 'script', 'facebook-jssdk');
  }

  child.onMessage('setShareUrl', setShareUrl);
  child.sendMessage('getShareUrl', '1');

});

$(function() {
  var $locate = $('.btn.locate');
  $locate.toggleClass('hidden', !navigator.geolocation);

  $locate.on('click', function(e) {
    // find user's location
    e.preventDefault();

    function foundLocation(position) {
      lat = position.coords.latitude;
      lng = position.coords.longitude;
      window.location = '/councillor?lat=' + lat + '&lng=' + lng;
    }

    function noLocation() {
      $('.btn.locate span').text('Use your location');
      alert('Sorry, your browser was unable to determine your location.');
    }

    if (navigator.geolocation) {
      $('.btn.locate span').text('Locating...');
      navigator.geolocation.getCurrentPosition(foundLocation, noLocation, {timeout:10000});
    } else {
      noLocation();
    }
  });
});

$(function() {
  $('form.find-councillor').on('submit', function(e) {
    $('form.find-councillor [type=submit]').text('Searching...').prop('disabled', true);
  });
});

$(function() {
  if ($("#map").length > 0) {
    var map = new L.Map("map", {
      scrollWheelZoom: false,
      zoomControl: false,
    });
    map.attributionControl.setPrefix('');
    var osm = new L.TileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: 'Map © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 18
    });
    map.addLayer(osm);

    var wardId = $('#map').attr('data');
    var url = "http://mapit.code4sa.org/area/MDB:" + wardId + ".geojson?type=WD";

    $.getJSON(url).
      then(function(data) {
        var area = new L.GeoJSON(data);
        map.addLayer(area);
        map.fitBounds(area.getBounds());
      });
  }
});

$(function() {
  // typeahead
  var mapit = new Bloodhound({
    queryTokenizer: Bloodhound.tokenizers.whitespace,
    datumTokenizer: Bloodhound.tokenizers.whitespace,
    remote: {
      url: 'http://mapit.code4sa.org/address?partial=1&generation=1&type=WD&address=QUERY',
      wildcard: 'QUERY',
      transform: function(response) {
        var results = [];

        for (var i = 0; i < response.addresses.length; i++) {
          var address = response.addresses[i];

          for (var j = 0; j < address.areas.length; j++) {
            var area = response[address.areas[j]];
            results.push({
              'address': address.formatted_address,
              'ward_id': area.codes.MDB,
              'name': 'Ward ' + area.name,
            });
          }
        }

        return results;
      },
    }
  });

  var $q = $('form.find-councillor input[name=address]');
  $q.typeahead(
    {
      minLength: 5,
      highlight: false,
    },
    {
      name: 'mapit',
      source: mapit,
      display: 'address',
      templates: {
        suggestion: Handlebars.compile(
          '<div class="name">{{name}}<span class="address">{{address}}</span></div>'
        )
      }
    }
  ).on('typeahead:select', function(e, item) {
    $('form.find-councillor [type=submit]').text('Searching...').prop('disabled', true);
    window.location = '/councillor/ward-' + item.ward_id;
  });
});

$(function() {
  $('#suggest-modal form').on('submit', function(e) {
    e.preventDefault();

    var $form = $(e.target);
    $.post($form.attr('action'), $form.serialize());
    $('#suggest-modal').modal('hide');
    alert("Thanks for your suggestion, we'll take a look and update our data.");
  });
});
