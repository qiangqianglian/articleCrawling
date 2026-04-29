import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";

// 路由配置
const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("./views/Home.vue"),
  },
  {
    path: "/authors",
    name: "Authors",
    component: () => import("./views/Authors.vue"),
  },
  {
    path: "/articles/:authorName",
    name: "Articles",
    component: () => import("./views/Articles.vue"),
  },
  {
    path: "/search",
    name: "Search",
    component: () => import("./views/Search.vue"),
  },
  {
    path: "/ai-settings",
    name: "AISettings",
    component: () => import("./views/AISettings.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const app = createApp(App);
app.use(router);
app.mount("#app");
