import Features from "@/components/website/Features";
import Footer from "@/components/website/Footer";
import Header from "@/components/website/Header";
import Hero from "@/components/website/Hero";
import KeyFeatures from "@/components/website/KeyFeatures";
import Pricing from "@/components/website/Pricing";
import WhySkhokho from "@/components/website/WhySkhokho";

export default function Home() {
    return (
        <div className="min-h-screen flex flex-col">
            <Header />
            <Hero />
            <Features />
            <WhySkhokho />
            <KeyFeatures />
            <Pricing />
            <Footer />
        </div>
    );
}
