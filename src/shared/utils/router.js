import { linkPageStyle, unlinkPageStyles } from "../helpers/pageStyles";
import { ROUTE_CHANGE } from "../consts/events";
import { navigate } from "../helpers/navigate";

export { navigate };

export class Router {
  constructor(pages = []) {
    this.pages = pages;
    this.currentPage = null;

    window.addEventListener(ROUTE_CHANGE, (event) => {
      this.navigate(event.detail.pathname);
    });
  }

  addPage(page) {
    this.pages.push(page);
  }

  navigate(pathname) {
    if (!this.pages.length) {
      throw new Error("Pages not provided");
    }

    const page = this.pages.find((p) => p.pathname === pathname);

    if (!page) {
      return this.navigate(this.pages[0].pathname);
    }

    if (this.currentPage) {
      unlinkPageStyles(this.currentPage.pathname);
      this.currentPage.onUnmount?.(document);
    }

    if (location.pathname !== pathname) {
      history.pushState({}, "", pathname);
    }

    this.currentPage = page;
    linkPageStyle(this.currentPage.pathname);

    document.body.innerHTML = page.htmlString;
    document.title = page.title;

    this.currentPage.onUnmount = page.callback?.(document);
  }
}
