import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { UserProvider } from './context/UserContext';
import Splash from './screens/Splash/Splash';
import { OnboardGender, OnboardBudget, OnboardColours, OnboardOccasions } from './screens/Onboarding/Onboarding';
import DNAQuiz from './screens/DNAQuiz/DNAQuiz';
import DNAResult from './screens/DNAResult/DNAResult';
import IdentityCard from './screens/IdentityCard/IdentityCard';
import Home from './screens/Home/Home';
import ProductDetail from './screens/ProductDetail/ProductDetail';
import DecisionIntelligence from './screens/DecisionIntelligence/DecisionIntelligence';
import ReverseShopping from './screens/ReverseShopping/ReverseShopping';
import FashionMemory from './screens/FashionMemory/FashionMemory';
import Community from './screens/Community/Community';
import MyntraMuse from './components/MyntraMuse/MyntraMuse';
import './styles/global.css';

// Simple Phone Wrapper to make the desktop preview look good
function PhoneWrapper({ children }) {
  return (
    <div className="phone-frame">
      <div className="desktop-hint">Built for Hackathon Demo • 390x844px</div>
      {children}
    </div>
  );
}

export default function App() {
  return (
    <UserProvider>
      <Router>
        <PhoneWrapper>
          <Routes>
            <Route path="/" element={<Splash />} />
            
            {/* Onboarding Flow */}
            <Route path="/onboard/gender" element={<OnboardGender />} />
            <Route path="/onboard/budget" element={<OnboardBudget />} />
            <Route path="/onboard/colours" element={<OnboardColours />} />
            <Route path="/onboard/occasions" element={<OnboardOccasions />} />
            
            {/* DNA Flow */}
            <Route path="/quiz" element={<DNAQuiz />} />
            <Route path="/dna-result" element={<DNAResult />} />
            <Route path="/identity-card" element={<IdentityCard />} />
            
            {/* Core App */}
            <Route path="/home" element={<Home />} />
            <Route path="/product/:id" element={<ProductDetail />} />
            <Route path="/decision/:id" element={<DecisionIntelligence />} />
            <Route path="/reverse" element={<ReverseShopping />} />
            <Route path="/memory" element={<FashionMemory />} />
            <Route path="/community" element={<Community />} />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          <MyntraMuse />
        </PhoneWrapper>
      </Router>
    </UserProvider>
  );
}
