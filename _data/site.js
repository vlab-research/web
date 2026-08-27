export default {
  name: "Virtual Lab",
  legal: "Virtual Lab, LLC",
  url: "https://vlab.digital",
  email: "info@vlab.digital",
  github: "https://github.com/vlab-research",

  // C-055, VERIFIED — supplied by Nandan as co-author, not independently verified
  // (SSRN 403s every non-browser client). Long form:
  // https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5495148
  //
  // index.html carries this URL as a literal in two places, one of them inside a
  // data-claim-source line that check-claims.py reads. It is NOT templated from
  // here, deliberately: rewriting a source line into a variable would change a
  // string the claim checker validates, for no gain. This entry exists so
  // _data/schema.js does not become a second place the URL is typed.
  paper: {
    url: "https://ssrn.com/abstract=5495148",
    claim: "C-055",
  },
  description:
    "Population-representative survey samples, recruited through ad platforms. " +
    "You set the target distribution; ad budget moves between strata until the " +
    "achieved sample matches it. The method is published and the code is open.",
};
