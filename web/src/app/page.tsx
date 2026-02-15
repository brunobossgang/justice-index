"use client";

import Hero from "@/components/Hero";
import Callout from "@/components/Callout";
import Comparison from "@/components/Comparison";
import OffenseRanking from "@/components/OffenseRanking";
import Trend from "@/components/Trend";
import MapSection from "@/components/MapSection";
import Calculator from "@/components/Calculator";
import HumanCost from "@/components/HumanCost";
import Evidence from "@/components/Evidence";
import TakeAction from "@/components/TakeAction";
import About from "@/components/About";
import Nav from "@/components/Nav";

export default function Home() {
  return (
    <main>
      <Nav />
      <Hero />
      <Callout />
      <HumanCost />
      <Comparison />
      <OffenseRanking />
      <Trend />
      <MapSection />
      <Calculator />
      <Evidence />
      <TakeAction />
      <About />
    </main>
  );
}
