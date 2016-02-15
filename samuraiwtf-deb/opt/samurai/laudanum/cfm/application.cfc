<!---
/* *****************************************************************************
***
*** Laudanum Project
*** A Collection of Injectable Files used during a Penetration Test
***
*** More information is available at:
***  http://laudanum.professionallyevil.com/
***  laudanum@secureideas.net
***
***  Project Leads:
***         Kevin Johnson @secureideas <kjohnson@secureideas.net
***         Tim Medin @timmedin <tim@securitywhole.com>
***         John Sawyer @johnhsawyer <john@inguardians.com>
***
*** Copyright 2015 by The Laudanum Team
***
********************************************************************************
***
*** This file provides access to shell access on the system.
*** Sourced from http://www.bennadel.com/blog/726-coldfusion-application-cfc-tutorial-and-application-cfc-reference.htm
*** Modified by Tim Medin
***
********************************************************************************
*** This program is free software; you can redistribute it and/or
*** modify it under the terms of the GNU General Public License
*** as published by the Free Software Foundation; either version 2
*** of the License, or (at your option) any later version.
***
*** This program is distributed in the hope that it will be useful,
*** but WITHOUT ANY WARRANTY; without even the implied warranty of
*** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*** GNU General Public License for more details.
***
*** You can get a copy of the GNU General Public License from this
*** address: http://www.gnu.org/copyleft/gpl.html#SEC1^
*** You can also write to the Free Software Foundation, Inc., 59 Temple
*** Place - Suite 330, Boston, MA  02111-1307, USA.
***
***************************************************************************** */
--->

<cfcomponent
    displayname="Application"
    output="true"
    hint="Handle the application.">


    <!--- Set up the application. --->
    <cfset THIS.Name = "AppCFC" />
    <cfset THIS.ApplicationTimeout = CreateTimeSpan( 0, 0, 1, 0 ) />
    <cfset THIS.SessionManagement = true />
    <cfset THIS.SetClientCookies = false />


    <!--- Define the page request properties. --->
    <cfsetting
        requesttimeout="20"
        showdebugoutput="false"
        enablecfoutputonly="false"
        />


    <cffunction
        name="OnApplicationStart"
        access="public"
        returntype="boolean"
        output="false"
        hint="Fires when the application is first created.">

        <!--- Return out. --->
        <cfreturn true />
    </cffunction>


    <cffunction
        name="OnSessionStart"
        access="public"
        returntype="void"
        output="false"
        hint="Fires when the session is first created.">

        <!--- Return out. --->
        <cfreturn />
    </cffunction>


    <cffunction
        name="OnRequestStart"
        access="public"
        returntype="boolean"
        output="false"
        hint="Fires at first part of page processing.">

        <!--- Define arguments. --->
        <cfargument
            name="TargetPage"
            type="string"
            required="true"
            />

        <!--- Return out. --->
        <cfreturn true />
    </cffunction>


    <cffunction
        name="OnRequest"
        access="public"
        returntype="void"
        output="true"
        hint="Fires after pre page processing is complete.">

        <!--- Define arguments. --->
        <cfargument
            name="TargetPage"
            type="string"
            required="true"
            />

        <!--- Include the requested page. --->
        <cfinclude template="#ARGUMENTS.TargetPage#" />

        <!--- Return out. --->
        <cfreturn />
    </cffunction>


    <cffunction
        name="OnRequestEnd"
        access="public"
        returntype="void"
        output="true"
        hint="Fires after the page processing is complete.">

        <!--- Return out. --->
        <cfreturn />
    </cffunction>


    <cffunction
        name="OnSessionEnd"
        access="public"
        returntype="void"
        output="false"
        hint="Fires when the session is terminated.">

        <!--- Define arguments. --->
        <cfargument
            name="SessionScope"
            type="struct"
            required="true"
            />

        <cfargument
            name="ApplicationScope"
            type="struct"
            required="false"
            default="#StructNew()#"
            />

        <!--- Return out. --->
        <cfreturn />
    </cffunction>


    <cffunction
        name="OnApplicationEnd"
        access="public"
        returntype="void"
        output="false"
        hint="Fires when the application is terminated.">

        <!--- Define arguments. --->
        <cfargument
            name="ApplicationScope"
            type="struct"
            required="false"
            default="#StructNew()#"
            />

        <!--- Return out. --->
        <cfreturn />
    </cffunction>


    <cffunction
        name="OnError"
        access="public"
        returntype="void"
        output="true"
        hint="Fires when an exception occures that is not caught by a try/catch.">

        <!--- Define arguments. --->
        <cfargument
            name="Exception"
            type="any"
            required="true"
            />

        <cfargument
            name="EventName"
            type="string"
            required="false"
            default=""
            />

        <!--- Return out. --->
        <cfreturn />
    </cffunction>

</cfcomponent>
