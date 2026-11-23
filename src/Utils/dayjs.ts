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
  return locale ? obj.locale(locale) : obj;
};

export default dayjs;
