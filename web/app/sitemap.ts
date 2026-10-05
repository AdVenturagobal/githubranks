import type { MetadataRoute } from "next";
import { getMeta, listRepoPages } from "@/lib/data";
import { LANGS } from "@/lib/i18n";

export const dynamic = "force-static";

const BASE = process.env.SITE_URL ?? "https://gitrise.pages.dev";

export default function sitemap(): MetadataRoute.Sitemap {
  const meta = getMeta();
  const cats = ["global", ...(meta?.categories ?? []).map((c) => c.id)];
  const urls: MetadataRoute.Sitemap = [];
  for (const lang of LANGS) {
    urls.push({ url: `${BASE}/${lang}/`, changeFrequency: "daily", priority: 1 });
    urls.push({ url: `${BASE}/${lang}/about/`, changeFrequency: "monthly", priority: 0.3 });
    for (const c of cats) {
      urls.push({ url: `${BASE}/${lang}/board/${c}/`, changeFrequency: "daily", priority: 0.8 });
    }
    for (const { owner, name } of listRepoPages()) {
      urls.push({
        url: `${BASE}/${lang}/repo/${owner}/${name}/`,
        changeFrequency: "daily",
        priority: 0.6,
      });
    }
  }
  return urls;
}
