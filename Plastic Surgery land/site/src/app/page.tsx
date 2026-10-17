import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { HeroSection } from "@/components/three/HeroSection";
import { UtpSection } from "@/components/sections/UtpSection";
import { SurgeonSection } from "@/components/sections/SurgeonSection";
import { TeamSection } from "@/components/sections/TeamSection";
import { DirectionsSection } from "@/components/sections/DirectionsSection";
import { PriceSection } from "@/components/sections/PriceSection";
import { ClinicsSection } from "@/components/sections/ClinicsSection";
import { StepsSection } from "@/components/sections/StepsSection";
import { CasesSection } from "@/components/sections/CasesSection";
import { FaqSection } from "@/components/sections/FaqSection";
import { CtaSection } from "@/components/sections/CtaSection";

export default function Page() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <UtpSection />
        <SurgeonSection />
        <TeamSection />
        <DirectionsSection />
        <PriceSection />
        <ClinicsSection />
        <StepsSection />
        <CasesSection />
        <FaqSection />
        <CtaSection />
      </main>
      <Footer />
    </>
  );
}