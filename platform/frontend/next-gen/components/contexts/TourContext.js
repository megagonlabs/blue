import { createContext, useContext, useState } from "react";
const TourContext = createContext();
export const useTour = () => useContext(TourContext);
export const TourProvider = ({ children }) => {
    const [currentStep, setCurrentStep] = useState(0);
    const [isTourActive, setIsTourActive] = useState(false);
    const steps = [
        {
            id: "platform-onboarding-tour-navigation-menu",
            title: "Welcome to Blue!",
            content:
                "Welcome to the tour! We'll show you the main features, starting with the navigation menu, where you can access various Apps.",
            position: "right-start",
        },
        {
            id: "platform-onboarding-tour-user-settings",
            title: "User Settings",
            content:
                "Your personal settings and account sign-out are available here.",
            position: "right-end",
        },
    ];
    const startTour = () => {
        setIsTourActive(true);
        setCurrentStep(0);
    };
    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            endTour();
        }
    };
    const prevStep = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };
    const endTour = () => {
        setIsTourActive(false);
        setCurrentStep(0);
    };
    const value = {
        isTourActive,
        startTour,
        endTour,
        nextStep,
        prevStep,
        currentStep,
        steps,
    };
    return (
        <TourContext.Provider value={value}>{children}</TourContext.Provider>
    );
};
