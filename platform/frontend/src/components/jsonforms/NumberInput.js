import { useSocket } from "@/components/hooks/useSocket";
import { NumericInput } from "@blueprintjs/core";
import _ from "lodash";
import { useReducer } from "react";
import { sendSocketMessage } from "../helper";
const NumberAbbreviation = {
    BILLION: "b",
    MILLION: "m",
    THOUSAND: "k",
};
const NUMBER_ABBREVIATION_REGEX = /((\.\d+)|(\d+(\.\d+)?))(k|m|b)\b/gi;
const SCIENTIFIC_NOTATION_REGEX = /((\.\d+)|(\d+(\.\d+)?))(e\d+)\b/gi;
export default function NumberInput({
    uischema,
    handleChange,
    path,
    data,
    precision = 11,
    id,
}) {
    const { socket } = useSocket();
    const [, forceUpdate] = useReducer((x) => x + 1, 0);
    const expandScientificNotationTerms = (value) => {
        // leave empty strings empty
        if (!value) {
            return value;
        }
        return value.replace(
            SCIENTIFIC_NOTATION_REGEX,
            expandScientificNotationNumber
        );
    };

    const expandNumberAbbreviationTerms = (value) => {
        // leave empty strings empty
        if (!value) {
            return value;
        }
        return value.replace(
            NUMBER_ABBREVIATION_REGEX,
            expandAbbreviatedNumber
        );
    };

    // Adapted from http://stackoverflow.com/questions/2276021/evaluating-a-string-as-a-mathematical-expression-in-javascript
    const evaluateSimpleMathExpression = (value) => {
        // leave empty strings empty
        if (!value) {
            return value;
        }
        // parse all terms from the expression. we allow simple addition and
        // subtraction only, so we'll split on the + and - characters and then
        // validate that each term is a number.
        const terms = value.split(/[+-]/);
        // ex. "1 + 2 - 3 * 4" will parse on the + and - signs into
        // ["1 ", " 2 ", " 3 * 4"]. after trimming whitespace from each term
        // and coercing them to numbers, the third term will become NaN,
        // indicating that there was some illegal character present in it.
        const trimmedTerms = terms.map((term) => term.trim());
        const numericTerms = trimmedTerms.map((term) => +term);
        const illegalTerms = numericTerms.filter(isNaN);
        if (illegalTerms.length > 0) {
            return "";
        }
        // evaluate the expression now that we know it's valid
        let total = 0;
        // the regex below will match decimal numbers--optionally preceded by
        // +/- followed by any number of spaces—-including each of the
        // following:
        // ".1"
        // "  1"
        // "1.1"
        // "+ 1"
        // "-   1.1"
        const matches = value.match(/[+-]*\s*(\.\d+|\d+(\.\d+)?)/gi) || [];
        for (const match of matches) {
            const compactedMatch = match.replace(/\s/g, "");
            total += parseFloat(compactedMatch);
        }
        const roundedTotal = roundValue(total);
        return roundedTotal.toString();
    };

    const nanStringToEmptyString = (value) => {
        // our evaluation logic isn't perfect, so use this as a final
        // sanitization step if the result was not a number.
        return _.isEqual(value, "NaN") ? "" : value;
    };

    const expandAbbreviatedNumber = (value) => {
        if (!value) {
            return value;
        }
        const num = +value.substring(0, value.length - 1);
        const lastChar = value.charAt(value.length - 1).toLowerCase();
        let result;
        if (_.isEqual(lastChar, NumberAbbreviation.THOUSAND)) {
            result = num * 1e3;
        } else if (_.isEqual(lastChar, NumberAbbreviation.MILLION)) {
            result = num * 1e6;
        } else if (_.isEqual(lastChar, NumberAbbreviation.BILLION)) {
            result = num * 1e9;
        }
        const isValid = result != null && !isNaN(result);
        if (isValid) {
            result = roundValue(result);
        }
        return isValid ? result.toString() : "";
    };

    const expandScientificNotationNumber = (value) => {
        if (!value) {
            return value;
        }
        return (+value).toString();
    };

    const roundValue = (value) => {
        // round to at most two decimal places
        return Math.round(value * 10 ** precision) / 10 ** precision;
    };
    const handleConfirm = (value) => {
        let result = value;
        result = expandScientificNotationTerms(result);
        result = expandNumberAbbreviationTerms(result);
        result = evaluateSimpleMathExpression(result);
        result = nanStringToEmptyString(result);
        handleChange(path, _.toNumber(result));
        // the user could have typed a different expression that evaluates to
        // the same value. force the update to ensure a render triggers even if
        // this is the case.
        forceUpdate();
        if (!_.isEqual(socket.readyState, WebSocket.OPEN)) return;
        setTimeout(() => {
            sendSocketMessage(
                socket,
                JSON.stringify({
                    type: "INTERACTIVE_EVENT_MESSAGE",
                    stream_id: _.get(uischema, "props.streamId", null),
                    path: path,
                    form_id: _.get(uischema, "props.formId", null),
                    value: _.toNumber(result),
                    timestamp: performance.timeOrigin + performance.now(),
                })
            );
        }, 0);
    };
    const handleKeyDown = (event) => {
        if (_.isEqual(event.key, "Enter")) {
            handleConfirm(event.target.value);
        }
    };
    const handleBlur = (event) => {
        handleConfirm(event.target.value);
    };
    const handleValueChange = (_valueAsNumber, valueAsString) => {
        handleChange(path, valueAsString);
    };
    return (
        <NumericInput
            name={id}
            allowNumericCharactersOnly={false}
            onBlur={handleBlur}
            onKeyDown={handleKeyDown}
            onValueChange={handleValueChange}
            value={_.isNumber(data) || _.isString(data) ? data : ""}
            buttonPosition="none"
            size="large"
            fill
        />
    );
}
