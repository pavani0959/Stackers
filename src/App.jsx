import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';

import { UserProvider } from './context/UserContext';
import { useUser } from './context/useUser';

import Splash from './screens/Splash/Splash';
import {
  OnboardGender,
  OnboardBudget,
  OnboardColours,
  OnboardOccasions,
} from './screens/Onboarding/Onboarding';

import DNAQuiz from './screens/DNAQuiz/DNAQuiz';
import DNAResult from './screens/DNAResult/DNAResult';
import IdentityCard from './screens/IdentityCard/IdentityCard';
import Home from './screens/Home/Home';
import ProductDetail from './screens/ProductDetail/ProductDetail';
import DecisionIntelligence from './screens/DecisionIntelligence/DecisionIntelligence';
import ReverseShopping from './screens/ReverseShopping/ReverseShopping';
import FashionMemory from './screens/FashionMemory/FashionMemory';
import Community from './screens/Community/Community';
import Wishlist from './screens/Wishlist/Wishlist';
import Search from './screens/Search/Search';
import Profile from './screens/Profile/Profile';
import Cart from './screens/Cart/Cart';

import MyntraMuse from './components/MyntraMuse/MyntraMuse';
import ApiErrorState from './components/ApiErrorState/ApiErrorState';

// Simple Phone Wrapper to make the desktop preview look good
function AppShell({ children }) {
  const isPhone = new URLSearchParams(window.location.search).get('presentation') === 'phone';

  return (
    <div className={`app-shell ${isPhone ? 'phone-frame' : ''}`}>
      {children}
    </div>
  );
}

/*
 * This component is rendered inside UserProvider,
 * so it can safely use useUser().
 */
function AppRoutes() {
  const {
    profileLoading,
    profileError,
    refreshProfile,
  } = useUser();

  // Do not render routes while the profile is loading.
  if (profileLoading) {
    return (
      <AppShell>
        <div className="app-loading">
          Loading your fashion identity…
        </div>
      </AppShell>
    );
  }

  // Do not render routes when profile loading fails.
  if (profileError) {
    return (
      <AppShell>
        <ApiErrorState
          title="Unable to load your profile"
          error={profileError}
          onRetry={refreshProfile}
        />
      </AppShell>
    );
  }

  // The main application is rendered only after profile loading succeeds.
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Splash />} />

        {/* Onboarding Flow */}
        <Route
          path="/onboard/gender"
          element={<OnboardGender />}
        />
        <Route
          path="/onboard/budget"
          element={<OnboardBudget />}
        />
        <Route
          path="/onboard/colours"
          element={<OnboardColours />}
        />
        <Route
          path="/onboard/occasions"
          element={<OnboardOccasions />}
        />

        {/* DNA Flow */}
        <Route path="/quiz" element={<DNAQuiz />} />
        <Route path="/dna-result" element={<DNAResult />} />
        <Route path="/identity-card" element={<IdentityCard />} />

        {/* Core App */}
        <Route path="/home" element={<Home />} />
        <Route path="/product/:id" element={<ProductDetail />} />
        <Route
          path="/decision/:id"
          element={<DecisionIntelligence />}
        />
        <Route path="/reverse" element={<ReverseShopping />} />
        <Route path="/memory" element={<FashionMemory />} />
        <Route path="/community" element={<Community />} />
        <Route path="/wishlist" element={<Wishlist />} />
        <Route path="/search" element={<Search />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/cart" element={<Cart />} />


        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      <MyntraMuse />
    </AppShell>
  );
}

export default function App() {
  return (
    <UserProvider>
      <Router>
        <AppRoutes />
      </Router>
    </UserProvider>
  );
}