const {
    faCircleA,
    faServer,
    faHeadSideGear,
    faDatabase,
    faFolderOpen,
    faFile,
    faProjectDiagram,
    faArrowRightToArc,
    faArrowRightFromArc,
} = require("@fortawesome/pro-duotone-svg-icons");
const { vanillaRenderers } = require("@jsonforms/vanilla-renderers");
import BooleanRenderer, {
    BooleanTester,
} from "@/components/jsonforms/renderers/Boolean";
import ButtonRenderer, {
    ButtonTester,
} from "@/components/jsonforms/renderers/Button";
import EnumRenderer, {
    EnumTester,
} from "@/components/jsonforms/renderers/Enum";
import GroupRenderer, {
    GroupTester,
} from "@/components/jsonforms/renderers/Group";
import IntegerRenderer, {
    IntegerTester,
} from "@/components/jsonforms/renderers/Integer";
import LabelRenderer, {
    LabelTester,
} from "@/components/jsonforms/renderers/Label";
import LayoutRenderer, {
    LayoutTester,
} from "@/components/jsonforms/renderers/Layout";
import NumberRenderer, {
    NumberTester,
} from "@/components/jsonforms/renderers/Number";
import StringRenderer, {
    StringTester,
} from "@/components/jsonforms/renderers/String";
import UnknownRenderer, {
    UnknownTester,
} from "@/components/jsonforms/renderers/Unknown";
module.exports = {
    REGISTRY_TYPE_LOOKUP: {
        data: { icon: faServer, key: "source" },
        agent: { icon: faCircleA, key: "agent" },
    },
    SEARCH_LIST_TYPE_LOOKUP: {
        agent: { icon: faHeadSideGear },
        input: { icon: faArrowRightToArc },
        output: { icon: faArrowRightFromArc },
        source: { icon: faServer },
        database: { icon: faDatabase },
        collection: { icon: faFolderOpen },
        entity: { icon: faFile },
        relation: { icon: faProjectDiagram },
    },
    JSONFORMS_RENDERERS: [
        ...vanillaRenderers,
        { tester: GroupTester, renderer: GroupRenderer },
        { tester: LabelTester, renderer: LabelRenderer },
        { tester: BooleanTester, renderer: BooleanRenderer },
        { tester: EnumTester, renderer: EnumRenderer },
        { tester: LayoutTester, renderer: LayoutRenderer },
        { tester: StringTester, renderer: StringRenderer },
        { tester: NumberTester, renderer: NumberRenderer },
        { tester: IntegerTester, renderer: IntegerRenderer },
        { tester: ButtonTester, renderer: ButtonRenderer },
        { tester: UnknownTester, renderer: UnknownRenderer },
    ],
};
