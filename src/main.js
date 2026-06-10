import { homePage } from "./pages/home";
import { aboutUsPage } from "./pages/about";
import { offersPage } from "./pages/offers";
import { authPage } from "./pages/auth";
import { Router, navigate } from "./shared/utils/router";

const appRouter = new Router();
appRouter.addPage(homePage);
appRouter.addPage(aboutUsPage);
appRouter.addPage(offersPage);
appRouter.addPage(authPage);

navigate(location.pathname ?? "/home");
