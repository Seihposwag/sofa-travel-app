function Page(pathname, title, htmlString, callback) {
  return {
    pathname,
    title,
    htmlString,
    callback,
  };
}

export { Page };
