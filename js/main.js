(function vlab () {

  function setContent(content) {
    document
      .querySelectorAll('div.main > div')
      .forEach(el => el.classList.remove('visible'))

    document
      .querySelectorAll('nav li')
      .forEach(el => el.classList.remove('selected'))

    document
      .querySelector('nav li.' + content)
      .classList.add('selected')

    document
      .querySelector('div.main > div.' + content)
      .classList.add('visible')
  }

  var router = new Navigo(null);
  router
    .on({
      'documentation': function () {
        setContent('documentation');
      },
      '*': function () {
        setContent('overview')
      }
    })
    .resolve();  
})()
