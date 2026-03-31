{
  const SEARCH_BOX_ID = "search-box";
  const NO_RESULTS_MESSAGE_ID = "not-found";
  const SEARCH_RESULTS_CONTAINER_ID = "search-results";
  const QUERY_VARIABLE_URL_STRING = "query";

  const extractUrlQueryParameter = (fallback = '') => {
    const urlSearchParams = new URLSearchParams(window.location.search);
    const queryParameter = urlSearchParams.get(QUERY_VARIABLE_URL_STRING);
    return queryParameter === null ? fallback : queryParameter;
  }

  const setSearchBoxValue = (searchBoxValue) => {
    document
      .getElementById(SEARCH_BOX_ID)
      .setAttribute("value", searchBoxValue);
  }

  const showNoResultsMessage = () => {
    document
      .getElementById(NO_RESULTS_MESSAGE_ID)
      .style
      .display = "block";
  }

  const hideNoResultsMessage = () => {
    document
      .getElementById(NO_RESULTS_MESSAGE_ID)
      .style
      .display = "none";
  }

  const setSearchResultsHtml = (innerHtml) => {
    document
      .getElementById(SEARCH_RESULTS_CONTAINER_ID)
      .innerHTML = innerHtml;
  }

  const createPostListingHtml = (postItem) => {
    const dateLine = postItem.date ? `<div class='meta'>${postItem.date}</div>` : '';
    return `
      <div class="search-result-item">
        <h3>
          <a class='search-link' href='${postItem.url}'>${postItem.title}</a>
        </h3>
        ${dateLine}
        <p>${postItem.content.substring(0, 200)}...</p>
      </div>
    `;
  };

  const displaySearchResults = (results) => {
    setSearchResultsHtml(
      results
        .map(result => createPostListingHtml(window.store[result.ref]))
        .join('')
    );
  }

  const buildLunrIndex = () => {
    return lunr(function () {
      this.field("id");
      this.field("title", { boost: 10 });
      this.field("author");
      this.field("category");
      this.field("content");
      for (let key in window.store) {
        const postJson = window.store[key];
        this.add({
          "id": key,
          "title": postJson.title,
          "author": postJson.author,
          "category": postJson.category,
          "content": postJson.content
        });
      }
    });
  }

  const lunrIndex = buildLunrIndex();

  const performSearch = (searchTerm) => {
    hideNoResultsMessage();
    if (!searchTerm || searchTerm.trim() === '') {
      setSearchResultsHtml('');
      return;
    }
    try {
      const results = lunrIndex.search(searchTerm + '*');
      if (results.length === 0) {
        setSearchResultsHtml('');
        showNoResultsMessage();
      } else {
        displaySearchResults(results);
      }
    } catch (e) {
      setSearchResultsHtml('');
    }
  }

  // Live search on keyup
  const searchBox = document.getElementById(SEARCH_BOX_ID);
  if (searchBox) {
    searchBox.addEventListener('input', function() {
      performSearch(this.value);
    });

    // Also check URL query on load
    const urlQuery = extractUrlQueryParameter();
    if (urlQuery) {
      searchBox.value = urlQuery;
      performSearch(urlQuery);
    }

    searchBox.focus();
  }
};