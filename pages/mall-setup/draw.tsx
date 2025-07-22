import dynamic from "next/dynamic";
console.log("MallSetupDraw page loaded");

const MallMapDrawPage = dynamic(() => import("../../components/MallMapDrawPage"), {
  ssr: false,
  loading: () => <div style={{ color: 'orange', fontWeight: 'bold', fontSize: 24, margin: 16 }}>Loading drawing tool...</div>
});

export default function MallSetupDraw() {
  return (
    <div>
      <div style={{ color: "red", fontWeight: "bold", fontSize: 24, margin: 16 }}>
        DEBUG: MallSetupDraw page is rendering
      </div>
      <MallMapDrawPage />
    </div>
  );
} 