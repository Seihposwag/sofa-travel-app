export const navigate = (pathname) => {
  window.dispatchEvent(
    new CustomEvent("ROUTE CHANGE", {
      detail: {
        pathname,
      },
    }),
  );
};
