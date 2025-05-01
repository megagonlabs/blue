import { vanillaRenderers } from "@jsonforms/vanilla-renderers";
import ArrayRenderer, { ArrayTester } from "./ArrayRenderer";
import BooleanRenderer, { BooleanTester } from "./BooleanRenderer";
import ButtonRenderer, { ButtonTester } from "./ButtonRenderer";
import CalloutRenderer, { CalloutTester } from "./CalloutRenderer";
import EnumRenderer, { EnumTester } from "./EnumRenderer";
import GroupRenderer, { GroupTester } from "./GroupRenderer";
import IntegerRenderer, { IntegerTester } from "./IntegerRenderer";
import LabelRenderer, { LabelTester } from "./LabelRenderer";
import LayoutRenderer, { LayoutTester } from "./LayoutRenderer";
import MarkdownRenderer, { MarkdownTester } from "./MarkdownRenderer";
import NumberRenderer, { NumberTester } from "./NumberRenderer";
import StringRenderer, { StringTester } from "./StringRenderer";
import TableRenderer, { TableTester } from "./TableRenderer";
import TabsRenderer, { TabsTester } from "./TabsRenderer";
import UnknownRenderer, { UnknownTester } from "./UnknownRenderer";
import VegaRenderer, { VegaTester } from "./VegaRenderer";
export const JSONFORMS_RENDERERS = [
    ...vanillaRenderers,
    { tester: ArrayTester, renderer: ArrayRenderer },
    { tester: LabelTester, renderer: LabelRenderer },
    { tester: StringTester, renderer: StringRenderer },
    { tester: BooleanTester, renderer: BooleanRenderer },
    { tester: ButtonTester, renderer: ButtonRenderer },
    { tester: CalloutTester, renderer: CalloutRenderer },
    { tester: EnumTester, renderer: EnumRenderer },
    { tester: GroupTester, renderer: GroupRenderer },
    { tester: IntegerTester, renderer: IntegerRenderer },
    { tester: LayoutTester, renderer: LayoutRenderer },
    { tester: MarkdownTester, renderer: MarkdownRenderer },
    { tester: NumberTester, renderer: NumberRenderer },
    { tester: TableTester, renderer: TableRenderer },
    { tester: TabsTester, renderer: TabsRenderer },
    { tester: VegaTester, renderer: VegaRenderer },
    { tester: UnknownTester, renderer: UnknownRenderer },
];
