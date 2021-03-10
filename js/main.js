(function vlab () {

  function setContent(name) {
    document
      .querySelectorAll('div.main > div')
      .forEach(el => el.classList.remove('visible'))

    document
      .querySelectorAll('nav li')
      .forEach(el => el.classList.remove('selected'))

    document
      .querySelector('nav li.' + name)
      .classList.add('selected')

    document
      .querySelector('div.main > div#' + name)
      .classList.add('visible')
  }

  function _add_route(routes, route, name) {
    routes[route] = function () { setContent(name) }
    return routes
  }

  var router = new Navigo(null);
  var conf = [
    ['software', 'software'],
    ['studies', 'studies'],
    ['*', 'overview']
  ]

  router
    .on(conf.reduce(function (a, c) {
      return _add_route(a, c[0], c[1])
    }, {}))
    .resolve()
})()
