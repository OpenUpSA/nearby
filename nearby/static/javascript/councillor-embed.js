function CouncillorEmbed(options) {
  var url = options.url || 'http://nearby.code4sa.org/councillor/';
  if (options.qs) {
    url = url + options.qs;
  }

  var parent = new pym.Parent('councillor-iframe', url);

  // setup message handlers to allow the child to get our URL
  function getShareUrl(message) {
    parent.sendMessage('setShareUrl', options.shareUrl || window.location.href);
  }
  parent.onMessage('getShareUrl', getShareUrl);
}

if (typeof(CouncillorEmbedOptions) === 'undefined') {
  var CouncillorEmbedOptions = {};
}

CouncillorEmbed(CouncillorEmbedOptions);
