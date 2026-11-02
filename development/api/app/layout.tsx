import type { Metadata } from "next";
export const metadata:Metadata={title:"Echoing Green · Decision service",description:"Secure Jev decisions for Echoing Green."};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
