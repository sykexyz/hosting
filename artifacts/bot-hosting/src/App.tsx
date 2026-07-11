import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Route, Switch, Router as WouterRouter, useLocation } from 'wouter';
import { AnimatePresence, motion } from 'framer-motion';
import { Toaster } from 'sonner';

import Landing from '@/pages/Landing';
import Signup from '@/pages/Signup';
import Login from '@/pages/Login';
import Dashboard from '@/pages/Dashboard';
import AdminLogin from '@/pages/AdminLogin';
import AdminDashboard from '@/pages/AdminDashboard';

const queryClient = new QueryClient();

const pageVariants = {
  initial: { opacity: 0, y: 12, filter: 'blur(4px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.32, ease: 'easeOut' as const } },
  exit:    { opacity: 0, y: -8, filter: 'blur(4px)', transition: { duration: 0.2, ease: 'easeIn' as const } },
};

function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{ willChange: 'opacity, transform' }}
    >
      {children}
    </motion.div>
  );
}

function NotFound() {
  return (
    <PageWrapper>
      <div className="min-h-[100dvh] w-full flex items-center justify-center bg-background p-6">
        <div className="text-center glass-panel p-12 rounded-2xl">
          <h1 className="text-6xl font-bold text-white mb-4 shadow-[0_0_20px_rgba(255,255,255,0.2)]">404</h1>
          <p className="text-xl text-white/40">Terminal not found</p>
        </div>
      </div>
    </PageWrapper>
  );
}

function AnimatedRouter() {
  const [location] = useLocation();
  return (
    <AnimatePresence mode="wait">
      <Switch key={location} location={location}>
        <Route path="/" component={() => <PageWrapper><Landing /></PageWrapper>} />
        <Route path="/signup" component={() => <PageWrapper><Signup /></PageWrapper>} />
        <Route path="/login" component={() => <PageWrapper><Login /></PageWrapper>} />
        <Route path="/dashboard" component={() => <PageWrapper><Dashboard /></PageWrapper>} />
        <Route path="/admin-login" component={() => <PageWrapper><AdminLogin /></PageWrapper>} />
        <Route path="/admin" component={() => <PageWrapper><AdminDashboard /></PageWrapper>} />
        <Route component={NotFound} />
      </Switch>
    </AnimatePresence>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
          <AnimatedRouter />
        </WouterRouter>
        <Toaster
          position="bottom-right"
          toastOptions={{ duration: 4000 }}
          theme="dark"
        />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
