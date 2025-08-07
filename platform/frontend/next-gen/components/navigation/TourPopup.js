import {
    Button,
    ButtonVariant,
    Card,
    Elevation,
    EntityTitle,
    H3,
    Intent,
    Portal,
} from "@blueprintjs/core";
import {
    faArrowRightLong,
    faMemoCircleCheck,
    faXmarkLarge,
} from "@fortawesome/sharp-duotone-solid-svg-icons";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { usePopper } from "react-popper";
import { useTour } from "../contexts/TourContext";
import { FAIcon } from "../FAIcon";
const ArrowPointer = ({ targetElementId }) => {
    const [rotation, setRotation] = useState(0);
    const arrowRef = useRef(null);
    const calculateRotation = () => {
        const arrowElement = arrowRef.current;
        const targetElement = document.getElementById(targetElementId);
        if (!arrowElement || !targetElement) {
            return;
        }
        const arrowRect = arrowElement.getBoundingClientRect();
        const targetRect = targetElement.getBoundingClientRect();
        const arrowCenterX = arrowRect.left + arrowRect.width / 2;
        const arrowCenterY = arrowRect.top + arrowRect.height / 2;
        const targetCenterX = targetRect.left + targetRect.width / 2;
        const targetCenterY = targetRect.top + targetRect.height / 2;
        const deltaX = targetCenterX - arrowCenterX;
        const deltaY = targetCenterY - arrowCenterY;
        const angleRadians = Math.atan2(deltaY, deltaX);
        const angleDegrees = angleRadians * (180 / Math.PI);
        const currentRotation = rotation % 360;
        let rotationDelta = angleDegrees - currentRotation;
        if (rotationDelta > 180) {
            rotationDelta -= 360;
        }
        if (rotationDelta < -180) {
            rotationDelta += 360;
        }
        setRotation((prevRotation) => prevRotation + rotationDelta);
    };
    useEffect(() => {
        setTimeout(calculateRotation, 300);
    }, []);
    useEffect(() => {
        const targetElement = document.getElementById(targetElementId);
        if (!targetElement) {
            const timeoutId = setTimeout(calculateRotation, 300);
            return () => clearTimeout(timeoutId);
        }
        const resizeObserver = new ResizeObserver(calculateRotation);
        resizeObserver.observe(targetElement);
        calculateRotation();
        window.addEventListener("resize", calculateRotation);
        window.addEventListener("scroll", calculateRotation);
        return () => {
            resizeObserver.disconnect();
            window.removeEventListener("resize", calculateRotation);
            window.removeEventListener("scroll", calculateRotation);
        };
    }, [targetElementId, rotation]);
    return (
        <div ref={arrowRef}>
            <FAIcon
                size={25}
                icon={faArrowRightLong}
                style={{
                    transform: `rotate(${rotation}deg)`,
                    pointerEvents: "none",
                    transition: "transform 0.3s ease-out",
                }}
            />
        </div>
    );
};
const TourPopup = () => {
    const { isTourActive, currentStep, steps, nextStep, prevStep, endTour } =
        useTour();
    const [referenceElement, setReferenceElement] = useState(null);
    const [popperElement, setPopperElement] = useState(null);
    const { styles, attributes, update } = usePopper(
        referenceElement,
        popperElement,
        {
            placement: steps[currentStep]?.position || "auto",
            modifiers: [{ name: "offset", options: { offset: [0, 15] } }],
        }
    );
    useEffect(() => {
        let timeoutId;
        const checkForElement = () => {
            if (!isTourActive) {
                setReferenceElement(null);
                return;
            }
            const currentStepData = steps[currentStep];
            const targetElement = document.getElementById(currentStepData.id);
            if (targetElement) {
                setReferenceElement(targetElement);
                targetElement.scrollIntoView({
                    behavior: "smooth",
                    block: "center",
                });
                clearTimeout(timeoutId);
            } else {
                timeoutId = setTimeout(checkForElement, 300);
            }
        };
        checkForElement();
        return () => {
            clearTimeout(timeoutId);
        };
    }, [isTourActive, currentStep, steps, endTour]);
    useLayoutEffect(() => {
        if (!referenceElement || !update) return;
        const resizeObserver = new ResizeObserver(update);
        resizeObserver.observe(referenceElement);
        return () => {
            resizeObserver.disconnect();
        };
    }, [referenceElement, update]);
    const currentStepData = steps[currentStep];
    const lastStep = _.isEqual(currentStep, steps.length - 1);
    if (!isTourActive || !referenceElement) {
        return null;
    }
    return (
        <Portal>
            <Card
                {...attributes.popper}
                className="border-radius-10"
                interactive
                elevation={Elevation.THREE}
                ref={setPopperElement}
                style={{
                    ...styles.popper,
                    zIndex: 1000,
                    maxWidth: 400,
                }}
            >
                <div
                    style={{
                        marginBottom: 10,
                        display: "flex",
                        justifyContent: "space-between",
                    }}
                >
                    <EntityTitle
                        title={currentStepData.title}
                        heading={H3}
                        icon={
                            <ArrowPointer
                                targetElementId={currentStepData.id}
                            />
                        }
                    />
                    <Button
                        onClick={endTour}
                        variant={ButtonVariant.MINIMAL}
                        icon={<FAIcon icon={faXmarkLarge} />}
                    />
                </div>
                <p>{currentStepData.content}</p>
                {currentStep > 0 && (
                    <Button
                        text="Previous"
                        style={{ marginRight: 10 }}
                        onClick={prevStep}
                        variant={ButtonVariant.MINIMAL}
                    />
                )}
                <Button
                    icon={lastStep ? <FAIcon icon={faMemoCircleCheck} /> : null}
                    onClick={nextStep}
                    intent={Intent.PRIMARY}
                >
                    {lastStep ? "Finish" : "Next"}
                </Button>
            </Card>
        </Portal>
    );
};
export default TourPopup;
