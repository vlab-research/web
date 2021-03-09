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

  function registerHandler(name, path) {
    document
      .querySelector('nav li.' + name)
      .addEventListener('click', function (e) {
        e.preventDefault()
        router.navigate(path)
      })
  }

  var conf = [
    ['documentation', 'documentation', '/documentation'],
    ['studies', 'studies', '/studies'],
    ['*', 'overview', '']
  ]

  conf.forEach(function (c) { registerHandler(c[1], c[2]) })
  router
    .on(conf.reduce(function (a, c) {
      return _add_route(a, c[0], c[1])
    }, {}))
    .resolve()
})()
