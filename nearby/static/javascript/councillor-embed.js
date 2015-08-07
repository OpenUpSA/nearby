function CouncillorEmbed() {
  var parent = new pym.Parent('councillor-iframe', 'http://nearby.code4sa.org/councillor/');

  // setup message handlers to allow the child to get our URL
  function getParentUrl(message) {
    parent.sendMessage('parentUrl', window.location.href);
  }
  parent.onMessage('getParentUrl', getParentUrl);
}

CouncillorEmbed();
