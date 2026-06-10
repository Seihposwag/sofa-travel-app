const getStyleIdByPathname = (pathname) => {
  return `${pathname}-style`;
};

export const linkPageStyle = (pathname) => {
  const style = document.createElement("link");

  Object.assign(style, {
    id: getStyleIdByPathname(pathname),
    rel: "stylesheet",
    href: `/styles/${pathname}.css`,
  });

  document.head.appendChild(style);
};

export const unlinkPageStyles = (pathname) => {
  document.getElementById(getStyleIdByPathname(pathname))?.remove();
};
