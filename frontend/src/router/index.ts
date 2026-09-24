import { createRouter, createWebHistory } from "vue-router";
import AboutView from "@/views/AboutView.vue";
import AboutTheDataView from "@/views/AboutTheDataView.vue";
import FAQView from "@/views/FAQView.vue";
import UserGuideView from "@/views/UserGuideView.vue";
import HomeView from "@/views/HomeView.vue";
import HealthOutcomesView from "@/views/HealthOutcomesView.vue";
import PaymentRatesView from "@/views/PaymentRatesView.vue";
import ProjectView from "@/views/ProjectView.vue";
import SearchView from "@/views/SearchView.vue";
import SearchResultsView from "@/views/SearchResultsView.vue";
import InviteMemberView from "@/views/InviteMemberView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/about",
      name: "about",
      component: AboutView,
    },
    {
      path: "/aboutdata",
      name: "aboutdata",
      component: AboutTheDataView,
    },
    {
      path: "/faq",
      name: "faq",
      component: FAQView,
    },
    {
      path: "/userguide",
      name: "userguide",
      component: UserGuideView,
    },
    {
      path: "/healthoutcomes",
      name: "healthoutcomes",
      component: HealthOutcomesView,
    },
    {
      path: "/paymentrates",
      name: "paymentrates",
      component: PaymentRatesView,
    },
    {
      path: "/search",
      name: "search",
      component: SearchView,
    },
    {
      path: "/protected/projects",
      name: "protected-project",
      component: ProjectView,
      beforeEnter: (to: any, from: any, next: any) => {
        const user = import.meta.env.VITE_PRP_EMAIL;
        const headers = new Headers();
        if (user) {
          headers.append("prp-email", user);
        }

        fetch("/protected/api/v2/user", {
          method: "GET",
          headers: headers,
        })
          .then((res) => {
            if (!res.ok) {
              // Go back to previous page, fallback to home if no previous page
              return next(from.name ? from : { name: "/" });
            }
            return res.json();
          })
          .then((json) => {
            if (json?.id) {
              next();
            }
          })
          .catch((error) => {
            console.error("Error during authentication: ", error);
            // Go back to previous page, fallback to home if no previous page
            next(from.name ? from : { name: "/" });
          });
      },
    },
    {
      path: "/results",
      name: "results",
      component: SearchResultsView,
    },
    {
      path: "/invitemember",
      name: "invitemember",
      component: InviteMemberView,
    },
  ],
});

export default router;
