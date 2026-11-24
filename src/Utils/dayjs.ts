import dayjs from "dayjs";
import "dayjs/locale/ar";
import customParseFormat from "dayjs/plugin/customParseFormat";
import duration from "dayjs/plugin/duration";
import isBetween from "dayjs/plugin/isBetween";
import preParsePostFormat from "dayjs/plugin/preParsePostFormat";
import relativeTime from "dayjs/plugin/relativeTime";
import i18next from "i18next";

dayjs.extend(relativeTime);
dayjs.extend(duration);
dayjs.extend(customParseFormat);
dayjs.extend(isBetween);
dayjs.extend(preParsePostFormat);

/**
 * Levantine Arabic (Syria): Syriac month names and Eastern Arabic digits.
 * Only used for display — the global dayjs locale stays English so values
 * sent to the API (YYYY-MM-DD, ISO strings) keep Latin digits.
 */
const arabicLocale = dayjs.Ls.ar;
const levantineMonths =
  "كانون الثاني_شباط_آذار_نيسان_أيار_حزيران_تموز_آب_أيلول_تشرين الأول_تشرين الثاني_كانون الأول".split(
    "_",
  );

dayjs.locale(
  {
    ...arabicLocale,
    name: "ar-sy",
    months: levantineMonths,
    monthsShort: levantineMonths,
    meridiem: (hour: number) => (hour < 12 ? "ص" : "م"),
    // Keep Latin digits (the base "ar" locale converts to Eastern Arabic ones).
    preparse: (value: string) => value,
    postformat: (value: string) => value,
  } as ILocale,
  undefined,
  true,
);

const DISPLAY_LOCALES: Record<string, string> = { ar: "ar-sy" };

/** dayjs instance localised for on-screen display in the active UI language. */
export const displayDayjs = (date?: Parameters<typeof dayjs>[0]) => {
  const language = (i18next.language || "en").split("-")[0];
  const locale = DISPLAY_LOCALES[language];
  const obj = dayjs(date);
  if (!locale) return obj;
  const localised = obj.locale(locale);
  if (language !== "ar") return localised;
  // Arabic dates read year/month/day in Latin digits (2000/10/16), never month names.
  const format = localised.format.bind(localised);
  localised.format = (template?: string) =>
    format(template === undefined ? undefined : numericArabicDate(template));
  return localised;
};

const DATE_ORDERS =
  /\b(?:DD?\/MM?\/YY(?:YY)?|MMMM? DD?, YYYY|DD? MMMM? YYYY|DD?-MMMM?-YYYY|DD?-MM?-YYYY)\b/g;
const numericArabicDate = (template: string) =>
  template.replace(/\s*\[at\]\s*/g, " ").replace(DATE_ORDERS, "YYYY/MM/DD");

export default dayjs;
