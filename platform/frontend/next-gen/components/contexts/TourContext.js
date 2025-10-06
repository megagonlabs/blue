import _ from "lodash";
import { createContext, useContext, useState } from "react";
const TourContext = createContext();
export const useTour = () => {
    return useContext(TourContext);
};
export const TourProvider = ({ children }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTourActive, setIsTourActive] = useState(false);
    const [currentTourId, setCurrentTourId] = useState(null);
    const tours = {
        platform_onboarding_tour: [
            {
                elementQuery: "#navigation-menu",
                title: "Welcome to Blue!",
                content:
                    "Welcome to the tour! We'll show you the main features, starting with the navigation menu, where you can access various Apps.",
                position: "right-start",
            },
            {
                elementQuery: "#navigation-menu",
                title: "Sessions",
                content:
                    'A session is a live application instance with a group of agents. Click on "All Sessions" to view a list of sessions available to you.',
                position: "right-start",
            },
            {
                elementQuery: ".session-list-new-session-button",
                title: "New Session",
                content:
                    'There are two ways to create a new session: click "New session" here, or select "New Session" from the navigation menu below "All Sessions."',
                position: "top",
            },
            {
                elementQuery: "#user-settings",
                title: "User Settings",
                content:
                    "Your personal settings and account sign-out are available here.",
                position: "right-end",
            },
        ],
    };
    const currentSteps = tours[currentTourId] || [];
    const startTour = (tourId) => {
        if (_.has(tours, tourId)) {
            setIsTourActive(true);
            setCurrentTourId(tourId);
            setCurrentStep(0);
        }
    };
    const nextStep = () => {
        if (currentStep < currentSteps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            endTour();
        }
    };
    const prevStep = (skipped = 0) => {
        setCurrentStep(Math.max(0, currentStep - 1 - skipped));
    };
    const endTour = () => {
        setIsTourActive(false);
        setCurrentTourId(null);
        setCurrentStep(0);
    };
    const value = {
        isTourActive,
        startTour,
        endTour,
        nextStep,
        prevStep,
        currentStep,
        currentTourId,
        steps: currentSteps,
    };
    return (
        <TourContext.Provider value={value}>{children}</TourContext.Provider>
    );
};
