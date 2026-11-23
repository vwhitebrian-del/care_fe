import { format as formatDateFns } from "date-fns";
import { ar } from "date-fns/locale";
import i18n from "i18next";
import { displayDayjs } from "@/Utils/dayjs";

type DateArg = Parameters<typeof formatDateFns>[0];
type FormatOptions = NonNullable<Parameters<typeof formatDateFns>[2]>;

const ORDERS: [RegExp, string][] = [
  [/MMMM?,? d{1,2},? yyyy/g, "yyyy/MM/dd"],
  [/d{1,2} MMMM? yyyy/g, "yyyy/MM/dd"],
  [/dd?\/MM?\/yyyy/g, "yyyy/MM/dd"],
  [/MMMM? d{1,2}(?![a-z])/g, "MM/dd"],
  [/MMMM?/g, "MM"],
];

/** Arabic dates are numeric, year first (2000/10/16); no month names. */
const toArabicPattern = (pattern: string) => {
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
