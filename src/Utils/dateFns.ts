import { displayDayjs } from "@/Utils/dayjs";
import { format as formatDateFns } from "date-fns";
import { ar } from "date-fns/locale";
import i18n from "i18next";

type DateArg = Parameters<typeof formatDateFns>[0];
type FormatOptions = NonNullable<Parameters<typeof formatDateFns>[2]>;

const ORDERS: [RegExp, string][] = [
  [/P{1,4}(?=p)/g, "yyyy/MM/dd "],
  [/P{1,4}/g, "yyyy/MM/dd"],
  [/MMMM?,? d{1,2},? yyyy/g, "yyyy/MM/dd"],
  [/d{1,2} MMMM?,? yyyy/g, "yyyy/MM/dd"],
  [/dd?\/MM?\/yyyy/g, "yyyy/MM/dd"],
  [/MMMM? d{1,2}(?![a-z])/g, "MM/dd"],
  [/d{1,2} MMMM?(?![a-z])/g, "MM/dd"],
  [/MMMM?/g, "MM"],
  [/(yyyy\/MM\/dd|MM\/dd),\s*/g, "$1 "],
];

/** Arabic dates are numeric, year first (2000/10/16); no month names. */
const toArabicPattern = (pattern: string) => {
  // English connector words such as 'at' don't belong in numeric Arabic dates.
  pattern = pattern.replace(/\s*'at'\s*/g, " ");
  // Text in [brackets] or 'quotes' is literal and must stay untouched.
  return pattern
    .split(/('[^']*')/)
    .map((part) =>
      part.startsWith("'")
        ? part
        : ORDERS.reduce((acc, [re, to]) => acc.replace(re, to), part),
    )
    .join("");
};

/** date-fns `format` that follows the UI language (Arabic: numeric dates, ص/م). */
export function format(
  date: DateArg,
  pattern: string,
  options?: FormatOptions,
) {
  const isArabic = (i18n.language || "").startsWith("ar");
  if (!isArabic) return formatDateFns(date, pattern, options);
  return formatDateFns(date, toArabicPattern(pattern), {
    locale: ar,
    ...options,
  });
}

/** "2 hours ago" / "منذ ساعتين" in the UI language. */
export const timeAgo = (date: Parameters<typeof displayDayjs>[0]) =>
  displayDayjs(date).fromNow();

/** Drop-in for `Date#toLocaleDateString`; Arabic gives numeric year-first dates. */
export function toLocaleDate(
  date: Date | string | number,
  locales?: Intl.LocalesArgument,
  options?: Intl.DateTimeFormatOptions,
) {
  const d = date instanceof Date ? date : new Date(date);
  if (!(i18n.language || "").startsWith("ar"))
    return d.toLocaleDateString(locales, options);
  const noYear = options && options.month && options.year === undefined;
  return formatDateFns(d, noYear ? "MM/dd" : "yyyy/MM/dd");
}

/** Short date for pickers: "Nov 23, 2026" in English, "2026/11/23" in Arabic. */
export function shortDate(date: Date, year = true) {
  if (!(i18n.language || "").startsWith("ar"))
    return new Intl.DateTimeFormat(i18n.language, {
      day: "numeric",
      month: "short",
      ...(year ? { year: "numeric" } : {}),
    }).format(date);
  return formatDateFns(date, year ? "yyyy/MM/dd" : "MM/dd");
}
