import { formatPhoneNumberIntl as format } from "react-phone-number-input";

/**
 * International phone number for display. It is isolated left-to-right so the
 * "+" and digit groups keep their order inside right-to-left (Arabic) pages.
 */
export const formatPhoneNumberIntl = (value: string) => {
  const formatted = format(value);
  return formatted ? `⁦${formatted}⁩` : formatted;
};
